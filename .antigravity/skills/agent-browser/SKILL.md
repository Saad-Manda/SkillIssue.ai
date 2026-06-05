---
name: agent-browser
description: Automates browser interactions for web testing, form filling, screenshots, and data extraction using the agent-browser CLI and read_url_content.
---

# Browser Automation & Web Retrieval with Antigravity

## Quick Reference & Tool Selection

Antigravity has two primary methods for interacting with the web:

1. **`read_url_content` (Fast Retrieval)**: Use this built-in Antigravity tool for reading static documentation, API references, or public articles. It is instant and does not spin up a browser.
2. **`run_command` with `agent-browser` (Full Automation)**: Use this when you need to test interactive frontend UIs, fill forms, click buttons, bypass login walls, execute custom JavaScript, or capture screenshots/videos.

---

## Interactive Browser Automation (via `run_command`)

When testing a web UI, run `agent-browser` commands directly inside the terminal using the `run_command` tool.

### Core Testing Workflow
1. **Initialize & Navigate**:
   ```bash
   agent-browser open http://localhost:3000
   ```
2. **Scan Accessible Elements**:
   Get a list of interactive elements marked with reference IDs (`@e1`, `@e2`, etc.):
   ```bash
   agent-browser snapshot -i
   ```
3. **Interact with Elements**: Use the reference IDs from the snapshot to fill, click, or hover.
4. **Repeat Snapshots**: Always snapshot again after any page transition, modal trigger, or form submission, as reference IDs will reset.

---

### Command Guide

#### 1. Navigation
```bash
agent-browser open <url>      # Navigate to a URL
agent-browser back            # Go back one page
agent-browser forward         # Go forward one page
agent-browser reload          # Reload the page
agent-browser close           # Terminate browser session
```

#### 2. DOM Analysis & Interactive Elements
```bash
agent-browser snapshot            # Accessibility tree
agent-browser snapshot -i         # Interactive elements with @e refs (recommended)
agent-browser snapshot -c         # Compact tree
agent-browser snapshot -s "#main" # Scan inside CSS selector
```

#### 3. Simulating User Input (Uses @e refs)
```bash
agent-browser click @e1           # Click element
agent-browser dblclick @e1        # Double click
agent-browser hover @e1           # Hover mouse over element
agent-browser fill @e2 "my-text"   # Clear field and type text
agent-browser type @e2 "more-text" # Type text without clearing
agent-browser select @e3 "value"  # Select option from dropdown
agent-browser check @e4           # Check a checkbox
agent-browser uncheck @e4         # Uncheck a checkbox
```

#### 4. Keyboard Controls
```bash
agent-browser press Enter         # Press a key
agent-browser press Control+a     # Key combinations
agent-browser keydown Shift       # Press and hold key
agent-browser keyup Shift         # Release held key
```

#### 5. Scroll & Drag
```bash
agent-browser scroll down 500     # Scroll page vertically by 500px
agent-browser scrollintoview @e1  # Scroll element into view
agent-browser drag @e1 @e2        # Drag element 1 to element 2 location
```

#### 6. Retrieving DOM States & Attributes
```bash
agent-browser get text @e1        # Get visible text
agent-browser get html @e1        # Get innerHTML
agent-browser get value @e1       # Get input value
agent-browser get attr @e1 href   # Get specific attribute value
agent-browser get url             # Get current URL path
agent-browser get title           # Get page title
```

#### 7. Screenshots & Recording
Capture pages for visual verification or layout testing:
```bash
agent-browser screenshot          # Capture and output base64
agent-browser screenshot path.png # Save screenshot as file
agent-browser screenshot --full   # Capture entire scroll height
agent-browser record start ./demo.webm  # Start video recording
agent-browser record stop               # Stop video recording and save
```

#### 8. Synchronization & Waiting
```bash
agent-browser wait @e1                     # Wait until element appears
agent-browser wait 3000                    # Pause execution for 3000ms
agent-browser wait --text "Order Placed"   # Wait for specific page text
agent-browser wait --load networkidle      # Wait for network calls to finish
```

#### 9. Cookies & Web Storage
```bash
agent-browser cookies                     # Get all current cookies
agent-browser cookies set name value      # Set cookie value
agent-browser storage local               # Dump localStorage
agent-browser storage local set key val   # Write to localStorage
```

#### 10. Device Emulation & Geolocation
```bash
agent-browser set viewport 375 812        # Resize viewport (e.g., iPhone size)
agent-browser set device "iPhone 14"      # Set User Agent & characteristics
agent-browser set geo 37.7749 -122.4194   # Mock GPS coordinates
```

---

## Example Scenario: Interactive Login Flow

To automate testing a standard login page:

```bash
# Open URL
agent-browser open http://localhost:8123/login

# Get elements
agent-browser snapshot -i
# Output contains:
# [ref=e1] textbox "Email address"
# [ref=e2] password "Password"
# [ref=e3] button "Sign in"

# Fill credentials and click submit
agent-browser fill @e1 "test-user@domain.com"
agent-browser fill @e2 "securepass123"
agent-browser click @e3

# Wait for redirect
agent-browser wait --url "**/dashboard"
agent-browser wait --load networkidle

# Capture visual success
agent-browser screenshot dashboard-loaded.png
```
