// whatsapp_bot/history_manager.js
const fs = require('fs');
const path = require('path');

class HistoryManager {
    constructor() {
        this.historyFile = path.join(__dirname, '../output/message_history.json');
        this.history = this.loadHistory();
    }

    loadHistory() {
        try {
            if (fs.existsSync(this.historyFile)) {
                const data = fs.readFileSync(this.historyFile, 'utf-8');
                return JSON.parse(data);
            }
        } catch (error) {
            console.log('⚠️  Creating new history file...');
        }
        
        return {
            sent: {},           // phone: { name, date, status, category }
            not_on_whatsapp: {}, // phone: { name, date, checked }
            failed: {},          // phone: { name, date, attempts, last_error }
            blacklist: []        // Manual blacklist
        };
    }

    saveHistory() {
        try {
            fs.writeFileSync(this.historyFile, JSON.stringify(this.history, null, 2));
        } catch (error) {
            console.error('❌ Failed to save history:', error.message);
        }
    }

    hasBeenContacted(phone) {
        return this.history.sent[phone] !== undefined;
    }

    isNotOnWhatsApp(phone) {
        return this.history.not_on_whatsapp[phone] !== undefined;
    }

    isBlacklisted(phone) {
        return this.history.blacklist.includes(phone);
    }

    canRetry(phone, maxAttempts = 3) {
        const failed = this.history.failed[phone];
        if (!failed) return true;
        return failed.attempts < maxAttempts;
    }

    markAsSent(phone, name, category) {
        this.history.sent[phone] = {
            name,
            category,
            date: new Date().toISOString(),
            status: 'delivered'
        };
        
        // Remove from failed if it was there
        delete this.history.failed[phone];
        
        this.saveHistory();
    }

    markAsNotOnWhatsApp(phone, name) {
        this.history.not_on_whatsapp[phone] = {
            name,
            checked: new Date().toISOString()
        };
        this.saveHistory();
    }

    markAsFailed(phone, name, category, error) {
        if (!this.history.failed[phone]) {
            this.history.failed[phone] = {
                name,
                category,
                attempts: 0,
                first_attempt: new Date().toISOString()
            };
        }
        
        this.history.failed[phone].attempts++;
        this.history.failed[phone].last_error = error;
        this.history.failed[phone].last_attempt = new Date().toISOString();
        
        this.saveHistory();
    }

    addToBlacklist(phone) {
        if (!this.history.blacklist.includes(phone)) {
            this.history.blacklist.push(phone);
            this.saveHistory();
        }
    }

    getStats() {
        return {
            total_sent: Object.keys(this.history.sent).length,
            not_on_whatsapp: Object.keys(this.history.not_on_whatsapp).length,
            failed: Object.keys(this.history.failed).length,
            blacklisted: this.history.blacklist.length
        };
    }

    shouldSkip(phone) {
        if (this.isBlacklisted(phone)) {
            return { skip: true, reason: 'blacklisted' };
        }
        if (this.hasBeenContacted(phone)) {
            return { skip: true, reason: 'already_contacted' };
        }
        if (this.isNotOnWhatsApp(phone)) {
            return { skip: true, reason: 'not_on_whatsapp' };
        }
        if (!this.canRetry(phone)) {
            return { skip: true, reason: 'max_retries_reached' };
        }
        return { skip: false };
    }
}

module.exports = HistoryManager;
