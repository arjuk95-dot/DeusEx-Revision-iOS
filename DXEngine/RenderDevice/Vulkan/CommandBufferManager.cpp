
#include "Precomp.h"
#include <chrono>
#include <cstdio>
#ifdef DXE_IOS
using ProbeClock = std::chrono::steady_clock;
static double ProbeElapsed(ProbeClock::time_point t) { return std::chrono::duration<double,std::milli>(ProbeClock::now()-t).count(); }
#endif
#include "CommandBufferManager.h"
#include "VulkanRenderDevice.h"
#include <dxgpu/vulkanswapchain.h>
#include <dxgpu/vulkansurface.h>
#include <dxwidgets/core/widget.h>

CommandBufferManager::CommandBufferManager(VulkanRenderDevice* renderer) : renderer(renderer)
{
	SwapChain = VulkanSwapChainBuilder()
		.Create(renderer->Device.get());

	ImageAvailableSemaphore = SemaphoreBuilder()
		.DebugName("ImageAvailableSemaphore")
		.Create(renderer->Device.get());

	RenderFinishedFence = FenceBuilder()
		.DebugName("RenderFinishedFence")
		.Create(renderer->Device.get());

	TransferSemaphore.reset(new VulkanSemaphore(renderer->Device.get()));

	CommandPool = CommandPoolBuilder()
		.QueueFamily(renderer->Device.get()->GraphicsFamily)
		.DebugName("CommandPool")
		.Create(renderer->Device.get());

	FrameDeleteList = std::make_unique<DeleteList>();
}

CommandBufferManager::~CommandBufferManager()
{
	DeleteFrameObjects();
}

void CommandBufferManager::WaitForFrame()
{
	if (!FramePending)
		return;

#ifdef DXE_IOS
    const auto fenceStart = ProbeClock::now();
#endif
	VkResult result = vkWaitForFences(renderer->Device.get()->device, 1, &RenderFinishedFence->fence, VK_TRUE, std::numeric_limits<uint64_t>::max());
	if (result != VK_SUCCESS)
		throw std::runtime_error("vkWaitForFences failed");
	result = vkResetFences(renderer->Device.get()->device, 1, &RenderFinishedFence->fence);
	if (result != VK_SUCCESS)
		throw std::runtime_error("vkResetFences failed");

#ifdef DXE_IOS
    ProbeFenceMs += ProbeElapsed(fenceStart);
#endif
	FramePending = false;
	PendingDrawCommands.reset();
	PendingTransferCommands.reset();
	DeleteFrameObjects();
}

void CommandBufferManager::WaitForTransfer()
{
#ifdef DXE_IOS
    renderer->EnsureForeground();
#endif
	WaitForFrame();
	renderer->Uploads->SubmitUploads();

	if (TransferCommands)
	{
		TransferCommands->end();

		QueueSubmit()
			.AddCommandBuffer(TransferCommands.get())
			.Execute(renderer->Device.get(), renderer->Device.get()->GraphicsQueue, RenderFinishedFence.get());

		VkResult result = vkWaitForFences(renderer->Device.get()->device, 1, &RenderFinishedFence->fence, VK_TRUE, std::numeric_limits<uint64_t>::max());
		if (result != VK_SUCCESS)
			throw std::runtime_error("vkWaitForFences failed");
		result = vkResetFences(renderer->Device.get()->device, 1, &RenderFinishedFence->fence);
		if (result != VK_SUCCESS)
			throw std::runtime_error("vkResetFences failed");

		TransferCommands.reset();
	}
}

void CommandBufferManager::SubmitCommands(bool present, int presentWidth, int presentHeight, bool wait)
{
#ifdef DXE_IOS
    renderer->EnsureForeground();
#endif
	WaitForFrame();
	renderer->Uploads->SubmitUploads();

	// A window of no size (minimized) has nothing to present to
	if (present && (presentWidth <= 0 || presentHeight <= 0))
		present = false;

	if (present)
	{
		if (SwapChain->Lost() || RequestedWidth != presentWidth || RequestedHeight != presentHeight || UsingVsync != renderer->UseVSync || UsingHdr != renderer->Hdr)
		{
			// A fence covers a submit, not the present queued after it: the
			// old swapchain and its semaphores may still be in use until the
			// device is idle.
			vkDeviceWaitIdle(renderer->Device.get()->device);

#ifdef DXE_IOS
            ++ProbeRecreates;
#endif
			UsingVsync = renderer->UseVSync;
			UsingHdr = renderer->Hdr;
			RequestedWidth = presentWidth;
			RequestedHeight = presentHeight;
			renderer->Framebuffers->DestroySwapChainFramebuffers();
			// The surface itself lost (a compositor gone): the swapchain let
			// go, a new surface from the window, the dead one freed; the
			// swapchain was once remade on the dead surface every frame
			if (SwapChain->SurfaceLost())
			{
				SwapChain.reset();
				renderer->Device->Surface = std::make_shared<VulkanSurface>(renderer->Device->Instance, renderer->Viewport->CreateVulkanSurface(renderer->Device->Instance->Instance));
				SwapChain = std::make_shared<VulkanSwapChain>(renderer->Device.get());
			}
			SwapChain->Create(presentWidth, presentHeight, renderer->UseVSync ? 2 : 3, renderer->UseVSync, renderer->Hdr);
			renderer->Framebuffers->CreateSwapChainFramebuffers();

			RenderFinishedSemaphores.clear();
			for (int i = 0; i < SwapChain->ImageCount(); i++)
			{
				RenderFinishedSemaphores.push_back(SemaphoreBuilder()
					.DebugName("RenderFinishedSemaphore")
					.Create(renderer->Device.get()));
			}
		}

#ifdef DXE_IOS
        const auto acquireStart = ProbeClock::now();
#endif
        PresentImageIndex = SwapChain->AcquireImage(ImageAvailableSemaphore.get());
#ifdef DXE_IOS
        ProbeAcquireMs += ProbeElapsed(acquireStart);
#endif
		if (PresentImageIndex != -1)
		{
			renderer->DrawPresentTexture(presentWidth, presentHeight);
		}
	}

	if (TransferCommands)
	{
		TransferCommands->end();

		QueueSubmit()
			.AddCommandBuffer(TransferCommands.get())
			.AddSignal(TransferSemaphore.get())
			.Execute(renderer->Device.get(), renderer->Device.get()->GraphicsQueue);
	}

	if (DrawCommands)
		DrawCommands->end();

	QueueSubmit submit;
	if (DrawCommands)
	{
		submit.AddCommandBuffer(DrawCommands.get());
	}
	if (TransferCommands)
	{
		submit.AddWait(VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT, TransferSemaphore.get());
	}
	if (present && PresentImageIndex != -1)
	{
		submit.AddWait(VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT, ImageAvailableSemaphore.get());
		submit.AddSignal(RenderFinishedSemaphores[PresentImageIndex].get());
	}
#ifdef DXE_IOS
    const auto submitStart = ProbeClock::now();
#endif
	submit.Execute(renderer->Device.get(), renderer->Device.get()->GraphicsQueue, RenderFinishedFence.get());
#ifdef DXE_IOS
    ProbeSubmitMs += ProbeElapsed(submitStart);
#endif

	if (present && PresentImageIndex != -1)
	{
#ifdef DXE_IOS
        const auto presentStart = ProbeClock::now();
#endif
		SwapChain->QueuePresent(PresentImageIndex, RenderFinishedSemaphores[PresentImageIndex].get());
#ifdef DXE_IOS
        ProbePresentMs += ProbeElapsed(presentStart);
        if (++ProbeFrames == 120) {
            std::fprintf(stderr,"iOS Vulkan pacing: fence %.3f acquire %.3f submit %.3f present %.3f ms/frame; recreates %u, images %d, vsync %d; CPU-call times, not GPU timestamps\n",ProbeFenceMs/120,ProbeAcquireMs/120,ProbeSubmitMs/120,ProbePresentMs/120,ProbeRecreates,SwapChain->ImageCount(),int(UsingVsync));
            ProbeFrames=ProbeRecreates=0;
            ProbeFenceMs=ProbeAcquireMs=ProbeSubmitMs=ProbePresentMs=0;
        }
#endif
	}

	if (!wait)
	{
		// Leave the frame in flight: the CPU goes on to the next game tick
		// while the GPU draws this one. WaitForFrame collects it before
		// anything touches its buffers, images or descriptors again.
		FramePending = true;
		PendingDrawCommands = std::move(DrawCommands);
		PendingTransferCommands = std::move(TransferCommands);
		return;
	}

	VkResult result = vkWaitForFences(renderer->Device.get()->device, 1, &RenderFinishedFence->fence, VK_TRUE, std::numeric_limits<uint64_t>::max());
	if (result != VK_SUCCESS)
		throw std::runtime_error("vkWaitForFences failed");
	result = vkResetFences(renderer->Device.get()->device, 1, &RenderFinishedFence->fence);
	if (result != VK_SUCCESS)
		throw std::runtime_error("vkResetFences failed");

	DrawCommands.reset();
	TransferCommands.reset();
	DeleteFrameObjects();
}

VulkanCommandBuffer* CommandBufferManager::GetTransferCommands()
{
	if (!TransferCommands)
	{
		WaitForFrame();
		TransferCommands = CommandPool->createBuffer();
		TransferCommands->begin();
	}
	return TransferCommands.get();
}

VulkanCommandBuffer* CommandBufferManager::GetDrawCommands()
{
	if (!DrawCommands)
	{
		WaitForFrame();
		DrawCommands = CommandPool->createBuffer();
		DrawCommands->begin();
	}
	return DrawCommands.get();
}

void CommandBufferManager::DeleteFrameObjects()
{
	FrameDeleteList = std::make_unique<DeleteList>();
}
