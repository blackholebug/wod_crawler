from nonebot.command import CommandSession
from nonebot.experimental.plugin import on_command


__plugin_name__ = 'wod_assistant'
__plugin_usage__ = 'usage: send commands to fetch report'

async def get_trophies():
    
    return


@on_command('trophies', aliases=("战利品","汇报战果"), permission=lambda sender: (not sender.is_privatechat))
async def _(session: CommandSession):
    try:
        result = await get_trophies()
    except Exception as e:
        result = e.message
    await session.send(result)