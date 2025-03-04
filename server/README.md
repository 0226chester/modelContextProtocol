add this to claude_desktop_config.json
```json
{
  "mcpServers": {
    "browser-use": {
      "command": "python",
      "args": [
        "path:/browser-use-fast.py"
      ],
      "env": {
        "OPENAI_API_KEY": "key"        
      }
    }    
  }
}
```
