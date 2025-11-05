# Lua Corporation Bot - Commands

## 👥 User Commands

### General
- `!help` - Show all available commands
- `!help <category>` - Show commands for a specific category

### Roles
- `!roles` - Open role selection menu
- `!myroles` - Show your current roles

### Invites & Stats
- `!invites [@user]` - Check invite statistics (yours or another user's)
- `!mystats` - Show your detailed recruitment record

## 👨‍💼 Admin Commands

### Announcements
- `!setannounce #channel` - Set the announcement channel (Admin only, required for first setup)
  - Example: `!setannounce #announcements`
- `!announce <message>` - Post general announcements to the announcements channel
  - Requires: Administrator permission OR Announcement role (ID: 1435285314129231964)
- `!addnews <title> | <message>` - Post news with custom title and message
  - Example: `!addnews Server Update | We've added new features!`
  - Requires: Administrator permission OR Announcement role (ID: 1435285314129231964)
  - Supports image attachments

**Note:** The announcements channel is protected. Only messages sent via `!announce` or `!addnews` commands are allowed. All other messages will be automatically deleted with a private warning to the user.

### Ticket System Setup
- `!setup ticketpanel` - Create support ticket dropdown menu
- `!setup ticketlog <#channel>` - Set ticket logging channel

### Ticket Management (in ticket channels)
- `!ticket close` - Close current ticket
- `!ticket add <@user>` - Add user to ticket
- `!ticket remove <@user>` - Remove user from ticket
- `!ticket list` - List all open tickets

### Invite Management
- `!invitemod <@user> <amount>` - Modify user's invite count
- `!resetinvites [@user]` - Reset invite statistics
- `!cacheinvites` - Manually refresh invite cache

### Role Management
- `!rolestats` - Show role statistics
- `!reactionroles` - Set up reaction role message

### Welcome System
- `!assignrole [@user]` - Manually assign the member role to a user
- `!welcomestats` - Show server statistics and welcome system info

### Testing
- `!testwelcome [@user]` - Test welcome message
- `!testboost [@user]` - Test boost message
- `!testrole [@user]` - Test auto-role assignment

## 🎫 Ticket System (User Interface)

Use the dropdown menu in the ticket channel to create:
- ❓ **General Support** - Questions about the server or community
- ⚠️ **Report Issue** - Report problematic behavior or content
- 💡 **Suggestions** - Suggest new features or improvements
- 👨‍💼 **Admin Contact** - Direct contact with administration

## 📋 Command Prefix

All commands use the prefix: `!`

## 🔐 Permissions

- **User Commands** - Available to all members
- **Admin Commands** - Require Administrator permission
- **Ticket Commands** - Available to staff and ticket creators

## 🤖 Automated Features

### Auto-Role Assignment
- New members automatically receive the Member role (ID: 1417470579774197800) when joining
- No manual intervention required

### Announcement Channel Protection
- The announcements channel only accepts messages from `!announce` and `!addnews` commands
- Other messages are automatically deleted with a warning to the user
- Keeps the channel clean and professional
