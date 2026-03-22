# proxmox_dashboard
My Take on a proxmox dashboard

# Create a proxmox API Token:

## Step 1: Create the Token in Proxmox
1. Log into your Proxmox Web UI.
2. Go to Datacenter > Permissions > API Tokens.
3. Click Add.
    - User: root@pam
    - Token ID: dashboard (or whatever name you like)
    - Privilege Separation: Checked (recommended).
4. IMPORTANT: Copy the Secret immediately. It will never be shown again.

## Step 2: Give the Token Permissions
1. Go to Datacenter > Permissions.
2. Click Add > API Token Permission.
3. Path: / (This gives access to the whole cluster)
4. Token: Select the root@pam!dashboard token you just made.
5. Role: PVEAuditor (This is "Read Only" — perfect for a dashboard).

## For the links to work add them to the .env file 
```.env
MEDIA_LINK=""
TORRENT_LINK=""
NAS_LINK=""
CAMERA_LINK=""
TORRENT_FOLDERS_LINK=""
```