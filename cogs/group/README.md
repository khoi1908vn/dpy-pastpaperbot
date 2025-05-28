# Group Cog Examples

This directory contains examples of Discord.py group cogs, which organize multiple related commands under a single command group.

## What are Group Cogs?

Group cogs in Discord.py are extensions that organize multiple related commands under a single command group. This helps maintain a clean command structure and improves user experience by grouping related functionality.

## Example Group Cog

The `_example.py` file demonstrates a typical implementation of a Discord.py group cog:

```py
class _ExampleGroup(GroupCog, group_name='examplegroup'):
    # ...
```

This creates a command group called `examplegroup` in your Discord bot, and all commands within this cog will be accessed as subcommands under `/examplegroup`.

## Features Demonstrated

1. **Basic Group Structure**: How to set up a command group with multiple subcommands
2. **Command Organization**: Organizing related commands under a single namespace
3. **Permission Handling**: Implementing permission checks for specific commands
4. **Parameter Handling**: Working with required and optional command parameters
5. **Embed Creation**: Creating rich embeds for command responses
6. **Logging**: Setting up proper logging for your cog

## Available Commands

The example includes several commands:

- `/examplegroup info` - Displays information about the command group
- `/examplegroup greet [user] [message]` - Greets a specified user with an optional custom message
- `/examplegroup admin` - An admin-only command that demonstrates permission checks

## How to Create Your Own Group Cog

1. Create a new Python file in this directory
2. Extend the `GroupCog` class and specify a `group_name`
3. Implement your commands using the `@command()` decorator
4. Implement the `setup()` function to register your cog with the bot

Example:

```python
from discord.ext.commands import GroupCog
from discord.app_commands import command

class _YourGroup(GroupCog, group_name='yourgroup'):
    def __init__(self, bot):
        self.bot = bot
        
    @command(name="yourcommand", description="Your command description")
    async def your_command(self, interaction):
        # Your command code here
        pass
        
async def setup(bot):
    await bot.add_cog(_YourGroup(bot))
```

## Best Practices

- Use clear, descriptive names for your command group and commands
- Add helpful descriptions to all commands and parameters
- Implement proper permission checks for administrative commands
- Use embeds for complex responses
- Set up appropriate logging for your cog
- Document your code thoroughly

## Logging Setup

The example demonstrates a comprehensive logging setup that you should include in your cogs:

```python
def setup_log(self):
    example_logger = logging.getLogger("cogs.group._example")
    example_logger.setLevel(logging.DEBUG)
    example_logger.addHandler(create_console_handler(logging.INFO))
    example_logger.addHandler(create_file_handler("./logs/cogs/group/_example", "_example"))
    self.logger = example_logger
```

### Key Components

1. **Logger Creation**
   - Create a logger with a namespace that reflects the cog's location (`cogs.group._example`)
   - This helps with identifying log messages in large applications

2. **Log Levels**
   - Set the base logger level to `DEBUG` to capture all levels of logs
   - Different log levels serve different purposes:
     - `DEBUG`: Detailed information for troubleshooting
     - `INFO`: Confirmation that things are working as expected
     - `WARNING`: Indication that something unexpected happened
     - `ERROR`: Error situations that should be investigated
     - `CRITICAL`: Critical errors that require immediate attention

3. **Console Handler**
   - Added with `INFO` level - only important messages appear in console
   - Console logs should be concise and focused on key information

4. **File Handler**
   - Logs everything to files in the `logs/cogs/group/_example` directory
   - File logs can be more verbose for detailed troubleshooting

### Effective Logging Practices

- **Log Command Invocations**

```python
self.logger.info(f"User {interaction.user} used command {command_name}")
```

- **Log Parameter Values**

```python
self.logger.debug(f"Command parameters: {parameter_name}={parameter_value}")
```

- **Log Decision Points**

```python
self.logger.debug(f"Condition evaluated: {condition_result}")
```

- **Log Errors with Context**

```python
self.logger.error(f"Error in command {command_name}: {error}", exc_info=True)
```

- **Include User Context**: Always include user IDs and relevant context to help with user support
