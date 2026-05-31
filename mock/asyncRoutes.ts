// 模拟后端动态生成路由
import { defineFakeRoute } from "vite-plugin-fake-server/client";
import { system, monitor, permission, frame, tabs } from "@/router/enums";
// 实时视频字幕生成
const RealtimeSubtitleGeneration = {
  path: "/index/page/",
  meta: {
    icon: "ep/menu",
    title: "实时字幕生成",
    rank: frame
  },
    children: [
      {
        path: "/index/page/",
        name: "RGPage",
        meta: {
          title: "实时字幕生成",
          frameSrc: "/index/page/",
          // keepAlive: true,
          roles: ["admin", "common"]
        }
      },
  ]
};

// 离线视频字幕生成
const OfflineSubtitleGeneration = {
  path: "/OfflineGenerate/",
  meta: {
    icon: "ep:monitor",
    title: "离线字幕生成",
    rank: frame
  },
    children: [
      {
        path: "/OfflineGenerate/",
        name: "OGPage",
        meta: {
          title: "离线字幕生成",
          frameSrc: "/OfflineGenerate/",
          // keepAlive: true,
          roles: ["admin", "common"]
        }
      },
  ]
};

// 离线去噪模块
const OfflineDenoising = {
  path: "/OfflineDenoising/",
  meta: {
    icon: "ri:window-line",
    title: "离线去噪",
    rank: frame
  },
    children: [
      {
        path: "/OfflineDenoising/",
        name: "ODPage",
        meta: {
          title: "离线去噪",
          frameSrc: "/OfflineDenoising/",
          // keepAlive: true,
          roles: ["admin", "common"]
        }
      },
  ]
};


// 硬字幕提取
const HardSubtitleExtraction = {
  path: "/HardSubtitleExtraction/",
  meta: {
    icon: "ri:links-fill",
    title: "硬字幕提取",
    rank: frame
  },
    children: [
      {
        path: "/HardSubtitleExtraction/",
        name: "HSPage",
        meta: {
          title: "硬字幕提取",
          frameSrc: "/HardSubtitleExtraction/",
          // keepAlive: true,
          roles: ["admin", "common"]
        }
      },
  ]
};

export default defineFakeRoute([
  {
    url: "/get-async-routes",
    method: "get",
    response: () => {
      return {
        success: true,
        data: [
          //RealtimeClientconfig,
          RealtimeSubtitleGeneration,
          OfflineSubtitleGeneration,
          OfflineDenoising,
          HardSubtitleExtraction
        ]
      };
    }
  }
]);
