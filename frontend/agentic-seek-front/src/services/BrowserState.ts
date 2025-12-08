export class BrowserState {
    private static instance: BrowserState;
    private currentHtml: string = "";
    private currentUrl: string = "";
    private lastUpdated: number = 0;

    private constructor() {}

    public static getInstance(): BrowserState {
        if (!BrowserState.instance) {
            BrowserState.instance = new BrowserState();
        }
        return BrowserState.instance;
    }

    public setPage(url: string, html: string) {
        this.currentUrl = url;
        this.currentHtml = html;
        this.lastUpdated = Date.now();
    }

    public getSnapshot() {
        return {
            url: this.currentUrl,
            html: this.currentHtml,
            timestamp: this.lastUpdated
        };
    }
}

export const browserState = BrowserState.getInstance();
