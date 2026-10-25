# GitHub AI 云端报告

仓库已创建，GitHub Pages 已发布，首次云端采集已成功（2026-10-25，1053 个候选）。**模型 API 调用与真实邮件投递尚未验证，等待补齐密钥。** 无需电脑持续开机；代码在 GitHub Actions 执行。

报告站点：https://okzhang2022.github.io/github-ai-reports/

当前待配置：Secrets `SMTP_PASSWORD`、`OPENAI_API_KEY`；Variables `MODEL`。163 的 SMTP 主机、465 端口及收发邮箱已配置。

## 你需要配置的内容

1. 一个你有管理权限的 GitHub 仓库。最容易部署的是新建公开仓库，例如 `github-ai-reports`。代码、快照、报告、README 证据都会公开；API Key、邮箱、SMTP 密码只放 Secrets。若选私有仓库，先确认你的 GitHub 套餐支持该仓库的 Pages，以及网站访问范围，私有仓库不意味着 Pages 网站私有。
2. 一个可用的 OpenAI API Key 和模型 ID。ChatGPT 订阅不能代替 API 账户计费。模型需要支持 Responses API 的 JSON 对象输出；每期最多整理十份 README，可能产生 API 费用。这里不预填未经验证的模型 ID，请在 API 账户中选择你实际可用的模型。
3. 一个支持 SMTP 的发件邮箱、SMTP 服务器地址、端口和应用专用密码/SMTP 授权码，以及收件邮箱。邮箱密码不要发到聊天中。优先用 465 SSL；587 使用 STARTTLS，不支持明文发送。
4. GitHub 已完成登录并授权公开发布。本仓库已经创建；下面的新建命令仅供重新部署参考，无需重复执行。

## 上传代码

下载旁边的 ZIP 后解压。确认 `.github/workflows/reports.yml` 也被上传，macOS 可以按 `⌘⇧.` 显示隐藏目录。

推荐终端操作（在解压后的 `github-ai-cloud` 目录运行）。先安装/准备 GitHub CLI，再执行：

```sh
gh auth login --hostname github.com --web
git init -b main
git add .
git commit -m "Set up GitHub AI reports"
gh repo create github-ai-reports --public --source=. --remote=origin --push
```

若仓库名已存在，换一个你自己的名称；不要覆盖现有项目。已有仓库可以把这些文件合入默认分支，注意 Actions 的定时触发只使用默认分支中的工作流。命令需要你在浏览器中完成 GitHub 登录，凭据留在你电脑，不要贴给助手。

## 设置 GitHub

进入新仓库：

- 工作流通过 YAML 显式声明保存数据所需权限，已验证可推送快照，无需扩大仓库所有工作流的默认权限。组织策略或分支保护若拒绝机器人推送，应检查对应规则，不要直接关闭组织保护。
- **Settings → Pages → Build and deployment → Source**：选择 **GitHub Actions**。
- **Settings → Secrets and variables → Actions**：按下面的表配置。
- 如 `github-pages` Environment 要求人工审批，每次发布会等待审批。全自动部署需设置适合该仓库的部署规则。

### Repository secrets

| 名称 | 填什么 |
|---|---|
| `OPENAI_API_KEY` | OpenAI API Key，仅放 Secret |
| `SMTP_USER` | SMTP 登录用户名，通常为发件邮箱 |
| `SMTP_PASSWORD` | SMTP 授权码/应用专用密码 |
| `MAIL_FROM` | 服务商允许的发件地址 |
| `MAIL_TO` | 接收报告的邮箱，可为单一邮箱 |

### Repository variables

| 名称 | 填什么 |
|---|---|
| `MODEL` | 你 API 账户实际可用、支持 Responses JSON 输出的模型 ID |
| `SITE_URL` | Pages 站点根地址，例如 `https://你的用户名.github.io/github-ai-reports`，不要加报告文件名 |
| `SMTP_HOST` | 邮箱服务商提供的 SMTP 主机 |
| `SMTP_PORT` | 通常 `465` 或 `587`，以服务商说明为准 |

GitHub 数据采集使用 Actions 自带的 `GITHUB_TOKEN`，不需要额外 PAT。不要把密钥写进 `config.json`、提交到 Git 或贴到聊天里。

## 首次启动与验收

1. 仓库 **Actions → GitHub AI reports → Run workflow**，选择 `mode=snapshot`。确认采集成功，默认分支出现 `data/snapshots/YYYY-MM-DD.json`。
2. 配置好变量和密钥后，选择 `mode=report`、`kind=weekly`。首次可能因“缺少期末边界快照”失败——这是有意拒绝编造上周数据，不能用今天的数字冒充上周末。
3. 如需立即验证 Pages 和 SMTP，在终端执行 `gh workflow run smoke.yml`，或 Actions 中运行 **Deployment and mail smoke test**。它只发布明确标注为历史试读的模板，并发送测试邮件，不生成任何新的增长排名，不调用模型。
4. 第二天采集后至少有两个快照。首个周一 09:00 会产生上一周期的部分窗口报告；拥有完整周起止日期快照后才标记为完整日期窗口。月、年同理，部署前数据不会自动补齐。
5. 联调完成后确认：Pages 页面可打开、测试邮件抵达、HTML 附件能打开、下一次到期的报告工作流成功。之后再停用旧 Codex 任务，避免迁移空档。当前交付没有停用本地任务。

完整报表的模型调用仍需到有可比较快照后验证。Smoke 测试只验证部署和邮件，不代表数据源和模型链路已验证。

## 时间与重试

| 操作 | 北京时间 | UTC cron |
|---|---|---|
| 每日 Star 快照 | 每天 00:05 | `5 16 * * *` |
| 周报 | 周一 09:00 | 每天 01:00 UTC 检查日期，周一执行 |
| 月报 | 1 日 09:00 | 同上，1 日执行 |
| 年报 | 1 月 1 日 09:00 | 同上，1 月 1 日执行 |
| 当日重试 | 09:20、09:40 | `20,40 1 * * *` |

重叠日期生成多份报告、分别发邮件。成功报告固定保存，正常重试不会重新调用模型；邮件成功后记发送标记。邮件发送与 Git 提交不具备跨系统事务，极少数在“SMTP 成功但标记提交失败”的情况下可能重复投递。

GitHub Actions 定时调度可能延迟、排队或漏执行，09:00 是计划启动时间，不是保证收信时间。报告生成与发布也需要时间。公开仓库长期没有活动可能被停用定时工作流，需检查 Actions 状态。失败时尝试 SMTP 告警；若 SMTP 本身故障，依靠 GitHub Actions 失败通知。请在个人 GitHub 通知设置中启用 Actions 失败邮件。

## 数据与选榜口径

- 从配置的 AI topics 搜索至少 100 Star 的仓库，每 topic 按总 Star 排序取前两页，合并并持续跟踪已发现候选。总 Star 只用于发现候选，**增长排名由两次快照差值计算**。
- 这不覆盖全站；低 Star、高速增长、缺少 topic 的新库可能被遗漏。修改 `config.json` 的 topics、pages_per_topic、min_stars 和 pinned_repositories 可扩展范围。超过显式的候选上限会失败，不会静默截断。
- 已发现候选持续刷新；新增候选没有期初数据就不纳入该期增长比较。删除/不可访问的已跟踪仓库会使采集失败，需检查原因后从历史候选策略中显式处理，不会当成“退出榜单”。
- 使用 Star **净增长**，不等于加星事件数。快照计划时间 00:05，采集有耗时与调度偏移，报告列出真实快照窗口，不声称精确午夜统计。
- 缺期初时采用周期内最早快照并明确标为“部分窗口”；缺期末日期快照则失败。仅有一个快照时生成数据积累状态报告，不凑前十和 Demo。
- 新上榜、升降与退出只比较相邻同类型、完整日期窗口且候选 ID 集合相同的报告，否则显示“暂无可比基线”。
- `data/reports` 保存结构化报告与模型使用的 README 证据，`site` 保存 HTML，便于追溯。年度快照可能逐步增加仓库存储和运行耗时，需留意 Actions 用量。

## 内容与 HTML

原模板完整保存在 `templates/reference.html`，CSS/交互从该模板提取。运行时生成的报告继续采用白底连续文档、固定左目录、青绿强调、移动端布局、复制和打印。

增长总览在前，每项含用途与输入输出、场景、受众、与你工作方向的关系、关注理由、Demo 目标、准备条件、安装/入口、步骤、示例输入、预期结果、限制、官方原文证据及“未实测”状态。独立历史总量榜不生成。期末总 Star 仅辅助展示。

模型只能依据官方 README 整理。脚本验证证据和安装命令必须确实出现在读取的 README 中，否则失败；所有模型文本按纯文本转义，不作为 HTML 执行。模型仍可能误解文档；不保证 Demo 实测成功，不虚构截图和运行结果。文档不足时会明确说明，不能自动创造接口。前 65,000 字符为模型证据范围，超长 README 的后部不参与整理。

## 本地检查

仅需 Python 3.12+，无第三方依赖：

```sh
python -m unittest discover -s tests -v
python -m py_compile src/report.py src/failure_mail.py
```

配置环境变量后可运行 `python src/report.py snapshot`、`python src/report.py build --kind weekly`。不要在未授权的本地环境运行 notify，它会真实发送邮件。

## 官方配置参考

- [GitHub Actions 定时事件](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
- [使用 Actions 发布 Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Repository Search API](https://docs.github.com/en/rest/search/search#search-repositories)
- [OpenAI Responses API](https://platform.openai.com/docs/api-reference/responses/create)

已验证 GitHub API 采集、Actions 数据持久化和 Pages HTTP 200。首次部署测试因缺少 SMTP 授权码停在邮件检查；模型接口和投递结果仍需在补齐配置后联调确认。
