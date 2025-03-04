import asyncio
import discord
import time
from discord.ext import commands
from discord.gateway import DiscordWebSocket

cooldown_messages = {}
message_timestamps = {}

GLOBAL_COOLDOWN_MESSAGES = {
    "user": "You are on cooldown for ",
    "guild": "This command is on cooldown for this server for "
}

def cool(bucket_type, tries, seconds, ignore=None, custom_messages=None):
    def decorator(func):
        cooldowns = {}

        async def wrapper(ctx, *args, **kwargs):
            key = ctx.author.id if bucket_type == "user" else ctx.guild.id if ctx.guild else ctx.author.id
            command_key = f"{key}_{ctx.command.name}"
            
            if ignore and callable(ignore):
                if ignore(ctx):
                    return await func(ctx, *args, **kwargs)

            current_time = time.time()
            
            if key in cooldowns:
                elapsed_time = current_time - cooldowns[key]['timestamp']
                if elapsed_time < seconds:
                    retry_after = seconds - elapsed_time
                    
                    if command_key not in message_timestamps or current_time - message_timestamps[command_key] > seconds:
                        messages = custom_messages or GLOBAL_COOLDOWN_MESSAGES
                        msg_template = messages["guild"] if bucket_type == "guild" else messages["user"]
                        
                        seconds_remaining = int(retry_after)
                        
                        embed = discord.Embed(
                            description=f"{msg_template}`{seconds_remaining}` seconds",
                            color=0x2F3136
                        )
                        cooldown_message = await ctx.send(embed=embed)
                        
                        message_timestamps[command_key] = current_time
                        
                        try:
                            await asyncio.sleep(3)
                            await cooldown_message.delete()
                        except:
                            pass
                            
                    return
                else:
                    del cooldowns[key]
            
            try:
                result = await func(ctx, *args, **kwargs)
                
                cooldowns[key] = {
                    'count': 1,
                    'timestamp': current_time
                }
                
                return result
            except Exception as e:
                raise e
                
        return wrapper
    return decorator

async def mobile_identify(self):
    payload = {
        "op": self.IDENTIFY,
        "d": {
            "token": self.token,
            "properties": {
                "$os": "Discord iOS",
                "$browser": "Discord iOS",
                "$device": "iOS",
                "$referrer": "",
                "$referring_domain": "",
            },
            "compress": True,
            "large_threshold": 250,
        },
    }

    if self.shard_id is not None and self.shard_count is not None:
        payload["d"]["shard"] = [self.shard_id, self.shard_count]

    state = self._connection
    
    if state._intents is not None:
        payload["d"]["intents"] = state._intents.value

    await self.call_hooks("before_identify", self.shard_id, initial=self._initial_identify)
    await self.send_as_json(payload)

DiscordWebSocket.identify = mobile_identify

class BucketType:
    user = "user"
    guild = "guild"

class Cooldown:
    def __init__(self, rate, per, type):
        self.rate = rate
        self.per = per
        self.type = type

class CommandOnCooldown(Exception):
    def __init__(self, retry_after, cooldown):
        self.retry_after = retry_after
        self.cooldown = cooldown

class Saint(commands.Bot):
    def __init__(self, prefix=",", blacklist=None):
        self.blacklist = blacklist
        intents = discord.Intents.all()
        super().__init__(command_prefix=prefix, intents=intents, case_insensitive=True, help_command=None)
        self.add_listener(self.on_command_error, 'on_command_error')

    def _get_bucket_type(self, bucket):
        if bucket == 'user':
            return commands.BucketType.user
        if bucket == 'guild':
            return commands.BucketType.guild
        raise ValueError("Invalid bucket type")

    async def on_ready(self):
        print(f"Bot is ready as {self.user}")
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.CustomActivity(name="🔗 discord.gg/saint")
        )

    async def process_commands(self, message):
        if self.blacklist and await self.blacklist(message.author):
            return
        await super().process_commands(message)

    def cmd(self, **kwargs):
        def decorator(func):
            cooldown = kwargs.get('cool', None)
            if cooldown:
                amount, per, bucket = cooldown
                func = cool(bucket, amount, per)(func)
            command = commands.Command(func, **kwargs)
            self.add_command(command)
            return func
        return decorator


__all__ = ['Saint', 'cool']