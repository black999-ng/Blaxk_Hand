// whatsapp_bot/bot.js
const {
    default: makeWASocket,
    useMultiFileAuthState,
    DisconnectReason,
    fetchLatestBaileysVersion,
    makeCacheableSignalKeyStore
} = require('@whiskeysockets/baileys');
const qrcode = require('qrcode-terminal');
const pino = require('pino');
const fs = require('fs');
const path = require('path');
const readline = require('readline');
const HistoryManager = require('./history_manager');

class WhatsAppBot {
    constructor() {
        this.sock = null;
        this.messagesFile = path.join(__dirname, '../output/phone_numbers.json');
        this.allMessages = [];
        this.history = new HistoryManager();
        this.delay = 5000;
        this.retryCount = 0;
        this.maxRetries = 5;
    }

    async start() {
        try {
            const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');
            const { version, isLatest } = await fetchLatestBaileysVersion();
            console.log(`📦 WA v${version.join('.')}, Latest: ${isLatest}`);

            this.sock = makeWASocket({
                version,
                auth: {
                    creds: state.creds,
                    keys: makeCacheableSignalKeyStore(
                        state.keys,
                        pino({ level: 'silent' })
                    )
                },
                logger: pino({ level: 'silent' }),
                printQRInTerminal: false,
                browser: ['Ubuntu', 'Chrome', '120.0.0'],
                connectTimeoutMs: 60000,
                defaultQueryTimeoutMs: 60000,
                keepAliveIntervalMs: 25000,
                generateHighQualityLinkPreview: false,
                syncFullHistory: false,
                markOnlineOnConnect: false,
                getMessage: async () => ({ conversation: '' })
            });

            this.setupEventHandlers(saveCreds);

        } catch (error) {
            console.error('❌ Init Error:', error.message);
            await this.retry();
        }
    }

    setupEventHandlers(saveCreds) {
        this.sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update;

            if (qr) {
                console.log('\n╔════════════════════════════════════╗');
                console.log('║  📱 SCAN QR CODE WITH WHATSAPP     ║');
                console.log('╚════════════════════════════════════╝\n');
                qrcode.generate(qr, { small: true });
                console.log('\n⏳ Waiting for scan...\n');
            }

            if (connection === 'close') {
                const statusCode = lastDisconnect?.error?.output?.statusCode;
                console.log(`\n❌ Connection closed (${statusCode})`);

                if (statusCode === DisconnectReason.loggedOut) {
                    console.log('⚠️  Logged out!');
                    console.log('   To fix: rm -rf auth_info_baileys\n');
                    process.exit(1);
                }

                // ✅ FIX: Don't auto-delete auth, just show message
                if (statusCode === 405) {
                    console.log('⚠️  Error 405: Method not allowed');
                    console.log('   WhatsApp rejected connection protocol');
                    console.log('\n💡 To fix:');
                    console.log('   1. rm -rf auth_info_baileys');
                    console.log('   2. npm update');
                    console.log('   3. node bot.js\n');
                    process.exit(1);
                }

                await this.retry();

            } else if (connection === 'open') {
                console.log('\n╔════════════════════════════════════╗');
                console.log('║  ✅ WHATSAPP CONNECTED!            ║');
                console.log('╚════════════════════════════════════╝\n');
                this.retryCount = 0;
                await this.sleep(2000);
                await this.loadMessages();
                await this.showMenu();

            } else if (connection === 'connecting') {
                console.log('🔄 Connecting...');
            }
        });

        this.sock.ev.on('creds.update', saveCreds);
    }

    async retry() {
        if (this.retryCount < this.maxRetries) {
            this.retryCount++;
            const wait = Math.min(this.retryCount * 3, 15);
            console.log(`🔄 Retry ${this.retryCount}/${this.maxRetries} in ${wait}s...\n`);
            await this.sleep(wait * 1000);
            this.start();
        } else {
            console.log('❌ Max retries reached.\n');
            console.log('💡 Try: rm -rf auth_info_baileys && node bot.js\n');
            process.exit(1);
        }
    }

    async loadMessages() {
        try {
            const data = fs.readFileSync(this.messagesFile, 'utf-8');
            const all = JSON.parse(data);

            this.allMessages = all.filter(msg => {
                return !this.history.shouldSkip(msg.phone).skip;
            });

            const skipped = all.length - this.allMessages.length;

            console.log('╔════════════════════════════════════╗');
            console.log('║  📋 LEADS LOADED                   ║');
            console.log('╚════════════════════════════════════╝');
            console.log(`   Total in file   : ${all.length}`);
            console.log(`   Already sent    : ${skipped}`);
            console.log(`   Ready to send   : ${this.allMessages.length}\n`);

        } catch (error) {
            console.error('❌ Cannot load messages:', error.message);
            console.log('💡 Run: python main.py first\n');
            process.exit(1);
        }
    }

    async showMenu() {
        const noWeb = this.allMessages.filter(m => !m.has_website);
        const withWeb = this.allMessages.filter(m => m.has_website);
        const stats = this.history.getStats();

        console.log('╔════════════════════════════════════════════╗');
        console.log('║       BLAXK\'s WhatsApp Campaign Menu       ║');
        console.log('╚════════════════════════════════════════════╝\n');

        console.log(`  1. 📧 Businesses WITHOUT websites`);
        console.log(`     → ${noWeb.length} new leads ready\n`);

        console.log(`  2. 🌐 Businesses WITH websites`);
        console.log(`     → ${withWeb.length} leads (review required)\n`);

        console.log(`  3. 📊 Statistics`);
        console.log(`     → ${stats.total_sent} sent all-time\n`);

        console.log(`  4. ❌ Exit\n`);

        const choice = await this.ask('Enter choice [1-4]: ');

        switch (choice.trim()) {
            case '1':
                await this.groupPreview(noWeb, 'WITHOUT websites');
                break;
            case '2':
                await this.websiteLockedGroup(withWeb);
                break;
            case '3':
                this.showStats();
                await this.showMenu();
                break;
            case '4':
                console.log('\n👋 Goodbye!\n');
                process.exit(0);
                break;
            default:
                console.log('\n⚠️  Invalid choice\n');
                await this.showMenu();
        }
    }

    async groupPreview(messages, label) {
        if (messages.length === 0) {
            console.log(`\n⚠️  No leads available in this group\n`);
            await this.sleep(2000);
            await this.showMenu();
            return;
        }

        console.log(`\n╔════════════════════════════════════════════╗`);
        console.log(`║  📋 Group: ${label}`.padEnd(45) + '║');
        console.log(`╚════════════════════════════════════════════╝\n`);

        console.log('  Businesses:\n');
        messages.forEach((msg, i) => {
            console.log(`  ${String(i + 1).padStart(3)}. ${msg.name.substring(0, 35).padEnd(35)}`);
            console.log(`       ⭐ ${msg.rating} (${msg.rating_count} reviews) | 📞 ${msg.phone}`);
        });

        console.log('\n  ─────────────────────────────────────────');
        console.log('  📝 Sample Message Preview:\n');
        const preview = messages[0].message;
        preview.split('\n').forEach(line => {
            console.log(`  ${line}`);
        });
        console.log('  ─────────────────────────────────────────\n');

        console.log(`  Total to send: ${messages.length} leads`);
        console.log(`  Delay between: ${this.delay / 1000} seconds\n`);

        console.log('  [P] Proceed & send all');
        console.log('  [B] Back to menu\n');

        const action = await this.ask('Choose: ');

        switch (action.trim().toLowerCase()) {
            case 'p':
                await this.sendMessages(messages);
                break;
            case 'b':
            default:
                await this.showMenu();
        }
    }

    async websiteLockedGroup(messages) {
        console.log('\n╔════════════════════════════════════════════╗');
        console.log('║  ⚠️  REVIEW REQUIRED                        ║');
        console.log('╚════════════════════════════════════════════╝\n');

        if (messages.length === 0) {
            console.log('  No leads with websites found.\n');
            await this.sleep(2000);
            await this.showMenu();
            return;
        }

        console.log('  These businesses have existing websites.');
        console.log('  Please review each website before outreach.\n');

        console.log('  Businesses:\n');
        messages.forEach((msg, i) => {
            console.log(`  ${String(i + 1).padStart(3)}. ${msg.name.substring(0, 30).padEnd(30)}`);
            console.log(`       🌐 ${msg.website || 'URL not captured'}`);
            console.log(`       ⭐ ${msg.rating} (${msg.rating_count} reviews)`);
            console.log(`       📞 ${msg.phone}\n`);
        });

        console.log('  ─────────────────────────────────────────');
        console.log('  💡 To unlock this group:');
        console.log('     Run: python review_websites.py');
        console.log('     Review AI audit results');
        console.log('     Then return here to send\n');
        console.log('  ─────────────────────────────────────────\n');

        console.log('  [S] Send anyway (skip review)');
        console.log('  [B] Back to menu\n');

        const action = await this.ask('Choose: ');

        switch (action.trim().toLowerCase()) {
            case 's':
                console.log('\n⚠️  Proceeding without review...\n');
                await this.groupPreview(messages, 'WITH websites');
                break;
            case 'b':
            default:
                await this.showMenu();
        }
    }

    async sendMessages(messages) {
        console.log('\n╔════════════════════════════════════════════╗');
        console.log('║  🚀 SENDING CAMPAIGN                       ║');
        console.log('╚════════════════════════════════════════════╝\n');

        let sent = 0, notOnWA = 0, failed = 0;

        for (let i = 0; i < messages.length; i++) {
            const msg = messages[i];

            console.log(`┌───────────────────────────────────────────┐`);
            console.log(`│ [${String(i + 1).padStart(2)}/${messages.length}] ${msg.name.substring(0, 32).padEnd(32)} │`);
            console.log(`│ 📞 ${msg.phone.padEnd(39)} │`);
            console.log(`│ 📂 ${String(msg.category).padEnd(39)} │`);
            console.log(`└───────────────────────────────────────────┘`);

            try {
                console.log('   🔍 Verifying number...');
                const [result] = await this.sock.onWhatsApp(msg.phone);

                if (!result?.exists) {
                    console.log('   ⚠️  Not registered on WhatsApp\n');
                    this.history.markAsNotOnWhatsApp(msg.phone, msg.name);
                    notOnWA++;
                    continue;
                }

                console.log('   📤 Sending message...');
                await this.sock.sendMessage(
                    `${msg.phone}@s.whatsapp.net`,
                    { text: msg.message }
                );

                console.log('   ✅ Message delivered!\n');
                this.history.markAsSent(msg.phone, msg.name, msg.category);
                sent++;

                if (i < messages.length - 1) {
                    process.stdout.write(`   ⏳ Waiting ${this.delay / 1000}s...`);
                    await this.sleep(this.delay);
                    process.stdout.write(' Done\n\n');
                }

            } catch (error) {
                console.error(`   ❌ Failed: ${error.message}\n`);
                this.history.markAsFailed(msg.phone, msg.name, msg.category, error.message);
                failed++;
                await this.sleep(2000);
            }
        }

        this.saveLog(messages, sent, notOnWA, failed);

        console.log('╔════════════════════════════════════════════╗');
        console.log('║  🎉 CAMPAIGN COMPLETE                      ║');
        console.log('╚════════════════════════════════════════════╝\n');
        console.log(`   ✅ Sent           : ${sent}`);
        console.log(`   ⚠️  Not on WA     : ${notOnWA}`);
        console.log(`   ❌ Failed         : ${failed}\n`);

        await this.sleep(2000);
        await this.showMenu();
    }

    showStats() {
        const stats = this.history.getStats();
        console.log('\n╔════════════════════════════════════════════╗');
        console.log('║  📊 ALL-TIME STATISTICS                    ║');
        console.log('╚════════════════════════════════════════════╝\n');
        console.log(`   ✅ Total Sent      : ${stats.total_sent}`);
        console.log(`   ⚠️  Not on WatsApp : ${stats.not_on_whatsapp}`);
        console.log(`   ❌ Failed          : ${stats.failed}`);
        console.log(`   🚫 Blacklisted     : ${stats.blacklisted}\n`);
    }

    saveLog(messages, sent, notOnWA, failed) {
        try {
            const timestamp = new Date().toISOString().replace(/:/g, '-').split('.')[0];
            const log = {
                timestamp,
                total: messages.length,
                sent,
                not_on_whatsapp: notOnWA,
                failed
            };
            const logPath = path.join(__dirname, `../output/session_${timestamp}.json`);
            fs.writeFileSync(logPath, JSON.stringify(log, null, 2));
            console.log(`💾 Session saved: session_${timestamp}.json\n`);
        } catch (e) {
            // Silent fail
        }
    }

    ask(question) {
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
        return new Promise(resolve => {
            rl.question(question, answer => {
                rl.close();
                resolve(answer);
            });
        });
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

console.log('\n╔════════════════════════════════════════════╗');
console.log('║       BLAXK\'s WhatsApp Bot v2.0            ║');
console.log('║    Professional Campaign Manager           ║');
console.log('╚════════════════════════════════════════════╝\n');

const bot = new WhatsAppBot();
bot.start().catch(err => {
    console.error('❌ Fatal:', err.message);
    process.exit(1);
});
