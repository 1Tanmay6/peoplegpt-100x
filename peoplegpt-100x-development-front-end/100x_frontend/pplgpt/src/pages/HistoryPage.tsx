import React, { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { motion } from 'framer-motion';
import { Topbar } from '@/components/Topbar';
import { Button } from '@/components/ui/button';
import { captureEvent } from '@/lib/posthog';

interface DownloadPaths {
  green?: string;
  blue?: string;
  grey?: string;
}

interface Hit {
  id: string;
  timestamp: string;
  status: 'completed' | 'pending' | 'error';
  downloadPaths: DownloadPaths;
}

const fetchHits = async (): Promise<Hit[]> => {
  const idsRes = await fetch('http://localhost:8000/hits');
  if (!idsRes.ok) throw new Error('Failed to fetch hits');
  const idList: string[] = await idsRes.json();

  const historyRes = await fetch('http://localhost:8000/get-history'); // <-- now GET
  if (!historyRes.ok) throw new Error('Failed to fetch history');
  const history = await historyRes.json();

  return idList.map(id => ({
    id,
    timestamp: new Date().toISOString(), // or set to null if you don’t want fake timestamps
    status: history[id] ? 'completed' : 'pending', // or infer some other logic
    downloadPaths: history[id]?.downloadPaths || {},
  }));
};

const downloadFile = (url?: string) => {
  if (url) {
    const a = document.createElement('a');
    a.href = url;
    a.download = '';
    a.click();
  }
};

const HitHistoryPage: React.FC = () => {
  const [hits, setHits] = useState<Hit[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const getHits = () => {
      fetchHits()
        .then(data => setHits(data))
        .catch(console.error)
        .finally(() => setLoading(false));
    };

    getHits();
    const interval = setInterval(getHits, 5000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    captureEvent('history_page_loaded');
    return () => {
      captureEvent('history_page_unloaded');
    };
  }, []);

  const completedCount = hits.filter(hit => hit.status === 'completed').length;
  return (
    <div>
      <Topbar />
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <motion.h1
        className="text-3xl font-semibold text-center"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        Job Processing History
      </motion.h1>

      <Card>
        <CardContent className="p-4">
          <div className="flex justify-between items-center">
            <span className="text-lg font-medium">Total Jobs: {hits.length}</span>
            <Badge variant="outline">Completed: {completedCount}</Badge>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-4">
          {loading ? (
            <Skeleton className="h-40 w-full" />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Timestamp</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Downloads</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {hits.map(hit => (
                  <TableRow key={hit.id}>
                    <TableCell>{hit.id}</TableCell>
                    <TableCell>{new Date(hit.timestamp).toLocaleString()}</TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          hit.status === 'completed'
                            ? 'default'
                            : hit.status === 'pending'
                            ? 'secondary'
                            : 'destructive'
                        }
                      >
                        {hit.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="space-x-2">
                      <Button
                        className="bg-green-600 hover:bg-green-700"
                        onClick={() => {
                          downloadFile(hit.downloadPaths?.green);
                          captureEvent('history_download_clicked', { fileType: 'passed' });
                        }}
                      >
                        Passed
                      </Button>
                      <Button
                        className="bg-red-700 hover:bg-red-800"
                        onClick={() => {
                          downloadFile(hit.downloadPaths?.blue);
                          captureEvent('history_download_clicked', { fileType: 'failed' });
                        }}
                      >
                        Failed
                      </Button>
                      <Button
                        className="bg-gray-500 hover:bg-gray-600"
                        onClick={() => {
                          downloadFile(hit.downloadPaths?.grey);
                          captureEvent('history_download_clicked', { fileType: 'all' });
                        }}
                      >
                        Complete
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
    </div>
  );
};

export default HitHistoryPage;
