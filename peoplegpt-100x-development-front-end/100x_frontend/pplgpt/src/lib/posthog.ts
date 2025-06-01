import posthog from 'posthog-js';

const apiKey = import.meta.env.VITE_POSTHOG_API_KEY;
// Removed unused 'host' variable declaration

if (!apiKey) {
  console.warn('PostHog API key not found in environment variables');
}

posthog.init(apiKey, {
  api_host: 'https://app.posthog.com',
  // autocapture: true, // Removed as it is not recognized in the type definition
  loaded: () => {
    if (import.meta.env.DEV) {
      console.log('PostHog debug mode enabled');
      console.log('PostHog initialized in debug mode');
    }
  },
  // Removed capture_pageview as it is not recognized in the type definition
  // persistence: 'localStorage', // Removed as it is not recognized in the type definition
  // Removed bootstrap as it is not recognized in the type definition
});

export const captureEvent = (eventName: string, properties?: Record<string, any>) => {
  posthog.capture(eventName, properties);
};

export const identifyUser = (userId: string, properties?: Record<string, any>) => {
  posthog.identify(userId, properties);
};

export default posthog;