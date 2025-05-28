# Single Cog Examples

This directory contains examples of Discord.py single cogs, which implement individual commands and event listeners.

## What are Single Cogs?

Single cogs in Discord.py are extensions that contain individual commands and event listeners. Unlike group cogs, single cogs do not group commands under a common namespace but instead register them as individual top-level commands.

## Example Single Cog

The `_example.py` file demonstrates a typical implementation of a Discord.py single cog:

```python
class ExampleCog(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.setup_log()
    # ...
```

This creates a cog with individual commands that can be accessed directly with their command name, like `/example`.

## Features Demonstrated

1. **Basic Cog Structure**: How to set up a standard Discord.py cog
2. **Event Handling**: Using the `@Cog.listener()` decorator to handle Discord events
3. **Command Registration**: Creating slash commands with the `@command()` decorator
4. **Logging Setup**: Configuring proper logging for your cog
5. **Bot Integration**: Integrating the cog with your bot instance

## Available Commands

The example includes:

- `/example` - A basic example command (placeholder implementation)

## Available Event Listeners

The example includes:

- `on_ready` - An event listener that triggers when the bot is ready (placeholder implementation)

## How to Create Your Own Single Cog

1. Create a new Python file in this directory
2. Extend the `Cog` class
3. Implement your commands using the `@command()` decorator
4. Implement event listeners using the `@Cog.listener()` decorator
5. Implement the `setup()` function to register your cog with the bot

Example:

```python
from discord.ext.commands import Cog
from discord.app_commands import command

class YourCog(Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} is ready!")
        
    @command(name="yourcommand", description="Your command description")
    async def your_command(self, interaction):
        # Your command code here
        await interaction.response.send_message("It works!")
        
async def setup(bot):
    await bot.add_cog(YourCog(bot))
```

## Best Practices

- Give your commands clear, descriptive names
- Add helpful descriptions to all commands and parameters
- Implement proper permission checks for administrative commands
- Set up appropriate logging for your cog
- Handle exceptions properly
- Document your code thoroughly
- Use deferred responses for commands that may take some time to process

## Common Patterns

- **Deferred Responses**:

  ```python
  await interaction.response.defer()
  # Do some processing...
  await interaction.followup.send("Result")
  ```

- **Permission Checks**:

  ```python
  @command()
  @checks.has_permissions(administrator=True)
  async def admin_command(self, interaction):
      # Admin-only code here
  ```

- **Command Parameters**:

  ```python
  @command()
  @describe(user="The user to greet")
  async def greet(self, interaction, user: discord.User):
      await interaction.response.send_message(f"Hello {user.mention}!")
  ```
