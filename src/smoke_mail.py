import datetime as dt
import os
from report import ROOT, TZ, read, notify
config = read(ROOT / 'config.json')
config['site_url'] = os.environ.get('SITE_URL') or config['site_url']
# This manual workflow is explicitly intended to send one test email per run.
marker = ROOT / 'data/reports/template-sample.sent'
marker.unlink(missing_ok=True)
notify(dict(slug='template-sample', title='GitHub AI 云端部署测试 · 非新报告',
            notice='这封邮件仅验证 Pages 和 SMTP。附件为 2026 W42 历史试读模板，不能作为新的增长榜单。', repos=[]), config)
