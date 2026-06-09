# KylinEcho

<div align="center">

**字幕生成与自动剪辑系统** | **Subtitle Generation & Auto-Editing System**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-%5E18.18.0%20%7C%20%5E20.9.0%20%7C%20%3E%3D22.0.0-brightgreen)](https://nodejs.org/)
[![pnpm](https://img.shields.io/badge/pnpm-%3E%3D9-blue)](https://pnpm.io/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.5-green)](https://vuejs.org/)

</div>

---

## 📖 项目介绍 | Project Overview

KylinEcho 是一个功能强大的**字幕生成与自动剪辑系统**，集成了现代化的Web前端、Electron桌面应用、以及高效的视频处理能力。该系统支持批量视频处理、自动字幕提取与生成、智能内容剪辑等核心功能。

KylinEcho is a powerful **subtitle generation and auto-editing system** that integrates a modern web frontend, Electron desktop applications, and efficient video processing capabilities. The system supports batch video processing, automatic subtitle extraction and generation, intelligent content editing, and more.

### ✨ 核心特性 | Key Features

- 🎬 **视频字幕提取** - Extract subtitles from video files automatically
- ✂️ **智能视频剪辑** - Intelligent video editing and clipping capabilities
- 🖥️ **跨平台支持** - Web UI + Electron desktop application
- ⚡ **高性能处理** - Optimized for batch video processing
- 🌍 **国际化支持** - Multi-language localization ready
- 📊 **可视化界面** - Rich UI with Element Plus & Tailwind CSS

---

## 🛠️ 技术栈 | Tech Stack

### Frontend Stack
- **Core Framework**: Vue.js 3.5+, Vite 6.3+
- **UI Framework**: Element Plus 2.9, Tailwind CSS 4.1
- **State Management**: Pinia 3.0
- **Type Safety**: TypeScript 5.8
- **Routing**: Vue Router 4.5
- **Internationalization**: Vue i18n 11.1

### Desktop Application
- **Framework**: Electron 37.2
- **Build Tool**: Vite 7.0

### Development Tools
- **Linting**: ESLint 9.25 + Prettier 3.5 + Stylelint 16.18
- **Testing**: TypeScript compiler + vue-tsc
- **Build**: Tailwind CSS 4.1 + PostCSS
- **Git Hooks**: Husky + Lint-staged + Commitlint

### Language Composition
| Language | Percentage | Purpose |
|----------|-----------|---------|
| Scheme | 34.3% | Logic and computation |
| Lex | 28.8% | Lexical analysis |
| Tree-sitter Query | 21.5% | Syntax parsing |
| Vue | 7.7% | UI components |
| TypeScript | 3.3% | Type-safe JavaScript |
| Python | 2.9% | Video processing backend |
| Other | 1.5% | Configuration & utilities |

---

## 🚀 快速开始 | Quick Start

### 前置要求 | Prerequisites

- Node.js: `^18.18.0` || `^20.9.0` || `>=22.0.0`
- pnpm: `>=9`

### 安装 | Installation

```bash
# Clone the repository
git clone https://github.com/Zjomo/KylinEcho.git
cd KylinEcho

# Install dependencies
pnpm install
```

### 开发 | Development

```bash
# Start development server
pnpm dev

# Run with debug mode
NODE_OPTIONS=--max-old-space-size=4096 pnpm dev

# Run Electron desktop application
cd modules/SystemElectron
pnpm electron:serve

# Type checking
pnpm typecheck

# Code quality checks
pnpm lint          # Run all linters
pnpm lint:eslint   # ESLint
pnpm lint:prettier # Prettier
pnpm lint:stylelint # Stylelint
```

### 构建 | Build

```bash
# Production build
pnpm build

# Staging build
pnpm build:staging

# Preview build
pnpm preview:build
```

---

## 📁 项���结构 | Project Structure

```
KylinEcho/
├── src/                          # Main application source
├── modules/
│   └── SystemElectron/          # Electron desktop application
├── public/                       # Static assets
├── types/                        # TypeScript type definitions
├── locales/                      # Internationalization files
├── mock/                         # Mock data for development
├── utils/                        # Utility functions
├── build/                        # Build configuration
├── Dockerfile                    # Docker containerization
├── vite.config.ts               # Vite configuration
├── tsconfig.json                # TypeScript configuration
├── eslint.config.js             # ESLint configuration
├── stylelint.config.js          # Stylelint configuration
└── package.json                 # Dependencies and scripts
```

---

## 🎯 主要依赖 | Key Dependencies

### UI & Visualization
- `element-plus`: Enterprise UI components
- `echarts`: Data visualization library
- `vxe-table`: Advanced table component
- `vue-json-pretty`: JSON visualization

### Video & Media
- `xgplayer`: Video player
- `wavesurfer.js`: Audio waveform visualization
- `vue-pdf-embed`: PDF viewing

### Utilities
- `axios`: HTTP client
- `pinia`: State management
- `day.js`: Date manipulation
- `sortablejs`: Drag-and-drop functionality
- `qrcode`: QR code generation

### Development
- `@commitlint/cli`: Commit message linting
- `@eslint/js`: JavaScript linting
- `@tailwindcss/vite`: Tailwind CSS integration
- `code-inspector-plugin`: Development inspection

---

## 📋 可用命令 | Available Commands

| Command | Description |
|---------|-------------|
| `pnpm dev` | Start development server |
| `pnpm build` | Build for production |
| `pnpm build:staging` | Build for staging environment |
| `pnpm preview` | Preview production build |
| `pnpm typecheck` | Run TypeScript type checking |
| `pnpm lint` | Run all linters and formatters |
| `pnpm lint:eslint` | Fix ESLint issues |
| `pnpm lint:prettier` | Format code with Prettier |
| `pnpm lint:stylelint` | Fix style issues |
| `pnpm clean:cache` | Clean cache and reinstall dependencies |

---

## 🐳 Docker 支持 | Docker Support

The project includes a `Dockerfile` for containerization. Build and run:

```bash
docker build -t kylinecho .
docker run -p 8080:8080 kylinecho
```

---

## 📦 环境配置 | Environment Configuration

The project supports multiple environment configurations:

- `.env` - Default configuration
- `.env.development` - Development environment
- `.env.production` - Production environment
- `.env.staging` - Staging environment

See the respective files for detailed configuration options.

---

## 🤝 贡献指南 | Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes following conventional commits (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Commit Convention
This project uses `commitlint` to enforce [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

Examples: `feat(video): add subtitle extraction`, `fix(ui): resolve layout issue`

---

## 📄 许可证 | License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 作者 | Author

**Zjomo**
- GitHub: [@Zjomo](https://github.com/Zjomo)

---

## 🙏 致谢 | Acknowledgments

- Built with [Vue Pure Admin](https://github.com/pure-admin/vue-pure-admin)
- UI powered by [Element Plus](https://element-plus.org/)
- Styled with [Tailwind CSS](https://tailwindcss.com/)

---

## 📞 支持 | Support

For issues, questions, or suggestions, please open an [Issue](https://github.com/Zjomo/KylinEcho/issues) on GitHub.

---

<div align="center">

Made with ❤️ by Zjomo

⭐ If you find this project helpful, please consider giving it a star!

</div>
