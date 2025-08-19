# ImageTools Usage Guide

## get_images Method

### Core Principles
- **Only use parameters that the user explicitly requests**
- **Do NOT add default values or assume values for parameters not mentioned**
- **Leave parameters as null if the user doesn't specify them**

### Usage Examples

#### 1. "Show me public images"
```json
{
  "visibility": "public"
}
```
- `status` and `name` are not set (null)

#### 2. "Show me active status images"  
```json
{
  "status": "active"
}
```
- `visibility` and `name` are not set (null)

#### 3. "Show me ubuntu images"
```json
{
  "name": "ubuntu"
}
```
- `status` and `visibility` are not set (null)

#### 4. "Show me public active images"
```json
{
  "visibility": "public",
  "status": "active"
}
```
- `name` is not set (null)

### Important Notes
- If user asks for "public images only", do NOT automatically set `status` to "active"
- If user asks for "list of images", leave all parameters as null
- When in doubt, ask the user for clarification rather than making assumptions
- Always respect the user's explicit requests and avoid adding unrequested filters
