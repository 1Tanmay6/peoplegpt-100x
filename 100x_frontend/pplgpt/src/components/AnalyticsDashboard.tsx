import { useEffect, useState } from 'react';
import posthog from 'posthog-js';
import { Card } from './ui/card';

interface AnalyticsData {
  totalJobs: number;
  avgProcessingTime: string;
  totalResumes: number;
  passRate: number;
  recentErrors: number;
}

interface PostHogJobEvent {
  event: string;
  properties: {
    resumes_processed?: number;
    passed_resumes?: number;
    processing_time?: string;
  };
}

export function AnalyticsDashboard() {
  const [data, setData] = useState<AnalyticsData>({
    totalJobs: 0,
    avgProcessingTime: '0:00',
    totalResumes: 0,
    passRate: 0,
    recentErrors: 0
  });

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const today = new Date();
        const thirtyDaysAgo = new Date(today.setDate(today.getDate() - 30));
        
        const events = await posthog.query({
          select: ['*'],
          from: 'events',
          where: {
            timestamp: { after: thirtyDaysAgo.toISOString() }
          }
        }) as PostHogJobEvent[];

        const jobCompletions = events.filter((e: PostHogJobEvent) => e.event === 'backend_job_completed');
        const errors = events.filter((e: PostHogJobEvent) => e.event === 'backend_job_error');
        
        const totalResumes = jobCompletions.reduce((acc: number, job: PostHogJobEvent) => 
          acc + (job.properties.resumes_processed || 0), 0);
        
        const totalPassed = jobCompletions.reduce((acc: number, job: PostHogJobEvent) => 
          acc + (job.properties.passed_resumes || 0), 0);

        const avgTimeInSecs = jobCompletions.reduce((acc: number, job: PostHogJobEvent) => {
          if (!job.properties.processing_time) return acc;
          const [mins, secs] = job.properties.processing_time.split(' min ')[1].split(' sec');
          return acc + (parseInt(mins) * 60 + parseInt(secs));
        }, 0) / (jobCompletions.length || 1); // Avoid division by zero

        const minutes = Math.floor(avgTimeInSecs / 60);
        const seconds = Math.floor(avgTimeInSecs % 60);

        setData({
          totalJobs: jobCompletions.length,
          avgProcessingTime: `${minutes}:${seconds.toString().padStart(2, '0')}`,
          totalResumes,
          passRate: totalResumes > 0 ? (totalPassed / totalResumes) * 100 : 0,
          recentErrors: errors.length
        });
      } catch (error) {
        console.error('Error fetching analytics:', error);
      }
    };

    fetchAnalytics();
    // Refresh every 5 minutes
    const interval = setInterval(fetchAnalytics, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
      <Card className="p-4">
        <h3 className="text-lg font-semibold mb-2">Total Jobs Processed</h3>
        <p className="text-3xl font-bold">{data.totalJobs}</p>
      </Card>
      
      <Card className="p-4">
        <h3 className="text-lg font-semibold mb-2">Average Processing Time</h3>
        <p className="text-3xl font-bold">{data.avgProcessingTime}</p>
      </Card>
      
      <Card className="p-4">
        <h3 className="text-lg font-semibold mb-2">Total Resumes Analyzed</h3>
        <p className="text-3xl font-bold">{data.totalResumes}</p>
      </Card>
      
      <Card className="p-4">
        <h3 className="text-lg font-semibold mb-2">Pass Rate</h3>
        <p className="text-3xl font-bold">{data.passRate.toFixed(1)}%</p>
      </Card>
      
      <Card className="p-4">
        <h3 className="text-lg font-semibold mb-2">Recent Errors</h3>
        <p className="text-3xl font-bold text-red-500">{data.recentErrors}</p>
      </Card>
    </div>
  );
}