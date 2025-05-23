'use client';

import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle, 
  CardDescription 
} from "@/components/ui/card";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts';

interface ApiMonitorProps {
  refreshInterval?: number;  // Refresh interval in ms (default: 10000)
}

interface ApiCall {
  id: string;
  tool_name: string;
  endpoint: string;
  method: string;
  status: string;
  status_code?: number;
  duration_ms?: number;
  start_time: string;
  retry_count: number;
  error_message?: string;
}

interface ApiStats {
  total_calls: number;
  active_calls: number;
  error_count: number;
  error_rate: number;
  avg_duration_ms: number;
  tools: Record<string, {
    calls: number;
    errors: number;
    total_duration_ms: number;
    avg_duration_ms: number;
  }>;
}

interface VisualizationData {
  timeline: Array<{
    time: string;
    total: number;
    success: number;
    error: number;
    tools: Record<string, number>;
  }>;
  top_tools: Array<[string, number]>;
  top_error_tools: Array<[string, number]>;
  status_summary: {
    success: number;
    error: number;
  };
}

interface ApiMonitorData {
  stats: ApiStats;
  recent_calls: ApiCall[];
  visualization: VisualizationData;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

const ApiMonitor: React.FC<ApiMonitorProps> = ({ refreshInterval = 10000 }) => {
  const [data, setData] = useState<ApiMonitorData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Fetch monitor data
  const fetchMonitorData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/monitor');
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const data = await response.json();
      setData(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      console.error('Error fetching API monitor data:', err);
    } finally {
      setLoading(false);
    }
  };
  
  // Fetch data on mount and set up refresh interval
  useEffect(() => {
    fetchMonitorData();
    
    const intervalId = setInterval(fetchMonitorData, refreshInterval);
    
    return () => clearInterval(intervalId);
  }, [refreshInterval]);
  
  // Format duration in ms to a readable string
  const formatDuration = (ms?: number) => {
    if (ms === undefined) return 'N/A';
    
    if (ms < 1000) {
      return `${ms.toFixed(2)} ms`;
    } else {
      return `${(ms / 1000).toFixed(2)} s`;
    }
  };
  
  // Format date string
  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'N/A';
    
    try {
      const date = new Date(dateStr);
      return date.toLocaleTimeString();
    } catch (err) {
      return dateStr;
    }
  };
  
  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'text-green-500';
      case 'error':
      case 'timeout':
        return 'text-red-500';
      case 'pending':
        return 'text-yellow-500';
      case 'retry':
        return 'text-orange-500';
      default:
        return 'text-gray-500';
    }
  };
  
  if (loading && !data) {
    return (
      <Card className="bg-white">
        <CardContent className="pt-6">
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
            <span className="ml-2 text-black">Loading API monitor data...</span>
          </div>
        </CardContent>
      </Card>
    );
  }
  
  if (error) {
    return (
      <Card className="bg-white">
        <CardHeader>
          <CardTitle className="text-black">API Monitor</CardTitle>
          <CardDescription className="text-gray-600">Error loading monitoring data</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-red-100 p-4 rounded border border-red-300 text-red-800">
            {error}
          </div>
        </CardContent>
      </Card>
    );
  }
  
  if (!data) {
    return (
      <Card className="bg-white">
        <CardHeader>
          <CardTitle className="text-black">API Monitor</CardTitle>
          <CardDescription className="text-gray-600">No data available</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-black">No API call data is available. This could mean no API calls have been made yet.</p>
        </CardContent>
      </Card>
    );
  }
  
  // Prepare data for pie chart
  const statusData = [
    { name: 'Success', value: data.stats.total_calls - data.stats.error_count },
    { name: 'Error', value: data.stats.error_count }
  ];
  
  // Prepare data for tool usage chart
  const toolData = Object.entries(data.stats.tools)
    .map(([name, stats]) => ({
      name,
      calls: stats.calls,
      errors: stats.errors,
      avgDuration: stats.avg_duration_ms
    }))
    .sort((a, b) => b.calls - a.calls)
    .slice(0, 5);  // Top 5 tools
    
  // Prepare timeline data
  const timelineData = data.visualization.timeline
    .map(item => ({
      time: item.time,
      success: item.success,
      error: item.error
    }))
    .filter(item => item.success > 0 || item.error > 0)  // Only show time periods with data
    .slice(-10);  // Last 10 time periods
  
  return (
    <Card className="w-full bg-white text-black">
      <CardHeader>
        <CardTitle className="text-black">API Call Monitor</CardTitle>
        <CardDescription className="text-gray-600">
          Track and analyze API calls made by the agent
        </CardDescription>
      </CardHeader>
      
      <CardContent className="max-w-5xl mx-auto">
        <Tabs defaultValue="overview">
          <TabsList className="mb-4 bg-gray-100">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="recent">Recent Calls</TabsTrigger>
            <TabsTrigger value="charts">Charts</TabsTrigger>
          </TabsList>
          
          {/* Overview Tab */}
          <TabsContent value="overview">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="bg-gray-50 p-4 rounded-lg shadow border border-gray-200">
                <h3 className="text-sm font-medium text-gray-600">Total Calls</h3>
                <p className="text-2xl font-bold text-black">{data.stats.total_calls}</p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg shadow border border-gray-200">
                <h3 className="text-sm font-medium text-gray-600">Active Calls</h3>
                <p className="text-2xl font-bold text-black">{data.stats.active_calls}</p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg shadow border border-gray-200">
                <h3 className="text-sm font-medium text-gray-600">Error Rate</h3>
                <p className="text-2xl font-bold text-black">{(data.stats.error_rate * 100).toFixed(1)}%</p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg shadow border border-gray-200">
                <h3 className="text-sm font-medium text-gray-600">Avg Response Time</h3>
                <p className="text-2xl font-bold text-black">{formatDuration(data.stats.avg_duration_ms)}</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium mb-2 text-black">Top Tools</h3>
                <div className="bg-gray-50 rounded-lg shadow border border-gray-200 p-4">
                  <table className="min-w-full">
                    <thead>
                      <tr>
                        <th className="px-2 py-2 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Tool</th>
                        <th className="px-2 py-2 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">Calls</th>
                        <th className="px-2 py-2 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">Errors</th>
                        <th className="px-2 py-2 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">Avg Time</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(data.stats.tools)
                        .sort((a, b) => b[1].calls - a[1].calls)
                        .slice(0, 5)
                        .map(([tool, stats]) => (
                          <tr key={tool} className="border-t">
                            <td className="px-2 py-2 whitespace-nowrap text-sm font-medium text-gray-900">{tool}</td>
                            <td className="px-2 py-2 whitespace-nowrap text-sm text-gray-500 text-right">{stats.calls}</td>
                            <td className="px-2 py-2 whitespace-nowrap text-sm text-right">
                              <span className={stats.errors > 0 ? 'text-red-500' : 'text-gray-500'}>
                                {stats.errors}
                              </span>
                            </td>
                            <td className="px-2 py-2 whitespace-nowrap text-sm text-gray-500 text-right">
                              {formatDuration(stats.avg_duration_ms)}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-medium mb-2 text-black">Calls Over Time</h3>
                <div className="bg-gray-50 rounded-lg shadow border border-gray-200 p-4" style={{ height: '240px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={timelineData}
                      margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
                    >
                      <XAxis dataKey="time" />
                      <YAxis allowDecimals={false} />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="success" stroke="#00C49F" strokeWidth={2} />
                      <Line type="monotone" dataKey="error" stroke="#FF8042" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </TabsContent>
          
          {/* Recent Calls Tab */}
          <TabsContent value="recent">
            <div className="bg-gray-50 rounded-lg shadow border border-gray-200 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-3 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Tool</th>
                      <th className="px-3 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Method</th>
                      <th className="px-3 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Endpoint</th>
                      <th className="px-3 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Status</th>
                      <th className="px-3 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Time</th>
                      <th className="px-3 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Duration</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {data.recent_calls.map((call) => (
                      <tr key={call.id} className="hover:bg-gray-50">
                        <td className="px-3 py-2 whitespace-nowrap text-sm font-medium text-gray-900">
                          {call.tool_name}
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-500">
                          <span className={call.method === 'GET' ? 'text-blue-600' : 'text-green-600'}>
                            {call.method}
                          </span>
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-500">
                          <div className="max-w-xs truncate" title={call.endpoint}>
                            {call.endpoint}
                          </div>
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap text-sm">
                          <span className={`${getStatusColor(call.status)}`}>
                            {call.status}
                            {call.status_code ? ` (${call.status_code})` : ''}
                          </span>
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-500">
                          {formatDate(call.start_time)}
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-500">
                          {formatDuration(call.duration_ms)}
                        </td>
                      </tr>
                    ))}
                    
                    {data.recent_calls.length === 0 && (
                      <tr>
                        <td colSpan={6} className="px-3 py-4 text-center text-sm text-gray-500">
                          No API calls recorded yet
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </TabsContent>
          
          {/* Charts Tab */}
          <TabsContent value="charts">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium mb-2 text-black">Success vs Error Rate</h3>
                <div className="bg-gray-50 rounded-lg shadow border border-gray-200 p-4" style={{ height: '240px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={statusData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {statusData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={index === 0 ? '#00C49F' : '#FF8042'} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-medium mb-2 text-black">Tool Usage</h3>
                <div className="bg-gray-50 rounded-lg shadow border border-gray-200 p-4" style={{ height: '240px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={toolData}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="calls" fill="#8884d8" name="Total Calls" />
                      <Bar dataKey="errors" fill="#FF8042" name="Errors" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
              
              <div className="md:col-span-2">
                <h3 className="text-lg font-medium mb-2 text-black">Response Times by Tool</h3>
                <div className="bg-gray-50 rounded-lg shadow border border-gray-200 p-4" style={{ height: '240px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={toolData}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip formatter={(value) => `${value.toFixed(2)} ms`} />
                      <Legend />
                      <Bar dataKey="avgDuration" fill="#00C49F" name="Avg Response Time (ms)" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
        
        <div className="mt-4 flex justify-end">
          <button
            onClick={fetchMonitorData}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Refresh Data
          </button>
        </div>
      </CardContent>
    </Card>
  );
};

export default ApiMonitor;