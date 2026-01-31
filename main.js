const { Plugin, Notice, PluginSettingTab, Setting } = require('obsidian');
const { exec } = require('child_process');
const path = require('path');

const DEFAULT_SETTINGS = {
    defaultTag: '',
    pythonPath: 'python3' // Default to using python3 from PATH
}

module.exports = class FlomoSyncLauncher extends Plugin {
    async onload() {
        await this.loadSettings();

        // Add a ribbon icon (sidebar)
        this.addRibbonIcon('refresh-cw', 'Sync Flomo', (evt) => {
            this.syncFlomo();
        });

        // Add a command (Cmd+P)
        this.addCommand({
            id: 'sync-flomo-manual',
            name: 'Sync Flomo Now',
            callback: () => {
                this.syncFlomo();
            }
        });

        // Add settings tab
        this.addSettingTab(new FlomoSyncLauncherSettingTab(this.app, this));
    }

    async loadSettings() {
        this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
    }

    async saveSettings() {
        await this.saveData(this.settings);
    }

    syncFlomo() {
        new Notice('🚀 Starting Flomo Sync...');
        
        // Use configured python path
        const pythonPath = this.settings.pythonPath;
        
        // Use the script located inside the plugin directory
        const adapter = this.app.vault.adapter;
        const basePath = adapter.basePath;
        // Adjust this if you change folder structure. Assuming flomo_sync.py is in the same folder as main.js
        const scriptPath = path.join(basePath, '.obsidian', 'plugins', 'flomo-sync-launcher', 'flomo_sync.py');
        
        // Default output path to a folder named "Flomo" in the vault root
        const outputDir = path.join(basePath, 'Flomo');

        // Construct command with arguments
        let cmd = `"${pythonPath}" "${scriptPath}" --output-dir "${outputDir}"`;
        
        if (this.settings.defaultTag) {
            cmd += ` --default-tag "${this.settings.defaultTag}"`;
        }

        console.log(`[Flomo Sync] Executing: ${cmd}`);

        exec(cmd, (error, stdout, stderr) => {
            if (error) {
                console.error(`exec error: ${error}`);
                new Notice(`❌ Sync Failed: ${error.message.substring(0, 100)}...`); 
                return;
            }
            
            console.log(`[Flomo Sync] stdout: ${stdout}`);
            if (stderr) console.warn(`[Flomo Sync] stderr: ${stderr}`);

            new Notice('✅ Flomo Sync Completed!');
        });
    }
}

class FlomoSyncLauncherSettingTab extends PluginSettingTab {
    constructor(app, plugin) {
        super(app, plugin);
        this.plugin = plugin;
    }

    display() {
        const { containerEl } = this;

        containerEl.empty();

        containerEl.createEl('h2', { text: 'Flomo Sync Settings' });

        new Setting(containerEl)
            .setName('Python Path')
            .setDesc('Absolute path to your Python executable (e.g. /usr/bin/python3 or /opt/homebrew/bin/python3)')
            .addText(text => text
                .setPlaceholder('python3')
                .setValue(this.plugin.settings.pythonPath)
                .onChange(async (value) => {
                    this.plugin.settings.pythonPath = value;
                    await this.plugin.saveSettings();
                }));

        new Setting(containerEl)
            .setName('Default Tag')
            .setDesc('Tag to automatically append to all synced memos (e.g. #flomo)')
            .addText(text => text
                .setPlaceholder('#flomo')
                .setValue(this.plugin.settings.defaultTag)
                .onChange(async (value) => {
                    this.plugin.settings.defaultTag = value;
                    await this.plugin.saveSettings();
                }));
    }
}
