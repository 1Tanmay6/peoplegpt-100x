declare module 'posthog-js' {
  interface PostHogEvent {
    event: string;
    properties: Record<string, any>;
    timestamp: string;
  }

  interface PostHogQuery {
    select: string[];
    from: string;
    where: {
      timestamp?: {
        after?: string;
        before?: string;
      };
      [key: string]: any;
    };
  }

  interface PostHog {
    init(apiKey: string, options?: { api_host?: string; loaded?: (posthog: PostHog) => void }): void;
    capture(eventName: string, properties?: Record<string, any>): void;
    identify(distinctId: string, properties?: Record<string, any>): void;
    query(query: PostHogQuery): Promise<PostHogEvent[]>;
  }

  const posthog: PostHog;
  export default posthog;
}