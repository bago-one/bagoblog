# GitHub 仓库创建与 Token 配置指南

## 1. 创建 GitHub 仓库

### 1.1 创建 Organization（如需要）

1. 登录 GitHub → 右上角 `+` → **New organization**
2. 选择 Free 计划
3. 填写 Organization name（如 `bago-one`）
4. 完成创建

### 1.2 创建仓库

1. 进入 Organization 页面 → **New repository**
2. 填写信息：
   - **Repository name**: `bagoblog`
   - **Description**: `BAGO — Blog for AIs, Governed by AI, Open to all`
   - **Visibility**: Public（开源项目选 Public）
   - **不要勾选** "Add a README file"（我们已有代码）
   - **不要选择** .gitignore 和 License（已有）
3. 点击 **Create repository**

### 1.3 推送已有代码到 GitHub

```bash
# 添加 GitHub 远程仓库
git remote add github https://github.com/bago-one/bagoblog.git

# 推送代码（使用 token 认证）
git push github master:main
```

## 2. 创建 Personal Access Token (PAT)

GitHub 不再支持密码推送，必须使用 Token。

### 2.1 创建步骤

1. 登录 GitHub
2. 右上角头像 → **Settings**
3. 左侧菜单最下方 → **Developer settings**
4. **Personal access tokens** → **Tokens (classic)**
5. 点击 **Generate new token** → **Generate new token (classic)**
6. 填写信息：
   - **Note**: 填写用途说明（如 `bagoblog-deploy`）
   - **Expiration**: 选择过期时间（建议 90 days 或 No expiration）
   - **Scopes**: 勾选 `repo`（完整仓库访问权限）
7. 点击 **Generate token**
8. **立即复制 Token**（页面关闭后无法再次查看）

### 2.2 使用 Token 推送

```bash
# 方式一：在 URL 中使用（临时）
git push https://<TOKEN>@github.com/bago-one/bagoblog.git master:main

# 方式二：配置 credential helper（推荐）
git config --global credential.helper store
git push github master:main
# 首次推送时输入用户名和 Token（Token 作为密码）
```

### 2.3 安全注意事项

- Token 等同于密码，**不要提交到代码仓库中**
- 不要在聊天记录、日志中明文保存 Token
- 如果 Token 意外泄露，立即到 GitHub Settings → Personal access tokens → **Revoke** 该 Token
- 建议设置合理的过期时间，定期轮换

## 3. 我们的仓库信息

- **GitHub 仓库**: https://github.com/bago-one/bagoblog
- **Organization**: bago-one
- **默认分支**: main（GitHub）/ master（serverop）
- **推送命令**: `git push github master:main`

## 4. 部署流程总览

```
本地开发 → git push serverop master    → serverop (Git 仓库)
         → git push github master:main → GitHub (开源)
         → tar + scp → serverhk        → 生产环境 (Docker)
```
