/**
 * Workflow Suggestions Component
 * Displays AI-powered workflow recommendations for incidents
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Loader2, Play, Star, Zap, Shield, Brain } from 'lucide-react';

interface WorkflowRecommendation {
    id: string;
    name: string;
    description: string;
    repository: string;
    match_score: number;
    security_score: number;
    ai_score: number;
    complexity_score: number;
    node_count: number;
    integrations: string[];
    categories: string[];
    reason: string;
}

interface WorkflowSuggestionsProps {
    incidentId: string;
    incidentDescription: string;
    incidentType?: string;
}

export function WorkflowSuggestions({
    incidentId,
    incidentDescription,
    incidentType
}: WorkflowSuggestionsProps) {
    const [recommendations, setRecommendations] = useState<WorkflowRecommendation[]>([]);
    const [totalWorkflows, setTotalWorkflows] = useState<number>(0);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchRecommendations();
    }, [incidentDescription]);

    const fetchRecommendations = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch('http://localhost:8000/api/workflows/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    incident_description: incidentDescription,
                    incident_type: incidentType,
                    limit: 5,
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to fetch recommendations');
            }

            const data = await response.json();
            setRecommendations(data.recommendations);
            setTotalWorkflows(data.total_workflows_available);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
            setLoading(false);
        }
    };

    const getCategoryIcon = (categories: string[]) => {
        if (categories.includes('security')) return <Shield className="h-4 w-4" />;
        if (categories.includes('ai')) return <Brain className="h-4 w-4" />;
        return <Zap className="h-4 w-4" />;
    };

    const getCategoryColor = (categories: string[]) => {
        if (categories.includes('security')) return 'bg-red-500/10 text-red-500 border-red-500/20';
        if (categories.includes('ai')) return 'bg-purple-500/10 text-purple-500 border-purple-500/20';
        return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
    };

    const getComplexityLabel = (score: number) => {
        if (score < 0.3) return 'Simple';
        if (score < 0.6) return 'Medium';
        return 'Complex';
    };

    const getComplexityColor = (score: number) => {
        if (score < 0.3) return 'bg-green-500/10 text-green-500';
        if (score < 0.6) return 'bg-yellow-500/10 text-yellow-500';
        return 'bg-orange-500/10 text-orange-500';
    };

    if (loading) {
        return (
            <Card className="border-border/40 bg-card/50 backdrop-blur">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Brain className="h-5 w-5" />
                        AI Workflow Suggestions
                    </CardTitle>
                </CardHeader>
                <CardContent className="flex items-center justify-center py-8">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </CardContent>
            </Card>
        );
    }

    if (error) {
        return (
            <Card className="border-border/40 bg-card/50 backdrop-blur">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Brain className="h-5 w-5" />
                        AI Workflow Suggestions
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-sm text-destructive">Error: {error}</p>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="border-border/40 bg-card/50 backdrop-blur">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Brain className="h-5 w-5" />
                    AI Workflow Suggestions
                </CardTitle>
                <CardDescription>
                    Powered by {totalWorkflows.toLocaleString()} pre-trained workflows
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                {recommendations.length === 0 ? (
                    <p className="text-sm text-muted-foreground">
                        No workflow recommendations found for this incident.
                    </p>
                ) : (
                    recommendations.map((workflow, index) => (
                        <div
                            key={workflow.id}
                            className="group relative rounded-lg border border-border/40 bg-background/50 p-4 transition-all hover:border-primary/40 hover:bg-background/80"
                        >
                            {/* Rank Badge */}
                            <div className="absolute -left-3 -top-3 flex h-8 w-8 items-center justify-center rounded-full bg-primary text-sm font-bold text-primary-foreground shadow-lg">
                                {index + 1}
                            </div>

                            {/* Header */}
                            <div className="mb-3 flex items-start justify-between gap-4">
                                <div className="flex-1">
                                    <h4 className="mb-1 font-semibold leading-tight">
                                        {workflow.name}
                                    </h4>
                                    <p className="text-xs text-muted-foreground line-clamp-2">
                                        {workflow.description || 'No description available'}
                                    </p>
                                </div>

                                {/* Match Score */}
                                <div className="flex items-center gap-1 rounded-full bg-primary/10 px-2 py-1 text-xs font-semibold text-primary">
                                    <Star className="h-3 w-3 fill-current" />
                                    {workflow.match_score.toFixed(1)}
                                </div>
                            </div>

                            {/* Badges */}
                            <div className="mb-3 flex flex-wrap gap-2">
                                {/* Category */}
                                <Badge
                                    variant="outline"
                                    className={`${getCategoryColor(workflow.categories)} flex items-center gap-1`}
                                >
                                    {getCategoryIcon(workflow.categories)}
                                    {workflow.categories[0]}
                                </Badge>

                                {/* Complexity */}
                                <Badge
                                    variant="outline"
                                    className={getComplexityColor(workflow.complexity_score)}
                                >
                                    {getComplexityLabel(workflow.complexity_score)}
                                </Badge>

                                {/* Node Count */}
                                <Badge variant="outline" className="bg-muted/50">
                                    {workflow.node_count} nodes
                                </Badge>

                                {/* Repository */}
                                <Badge variant="outline" className="bg-muted/50 text-xs">
                                    {workflow.repository.split('-').slice(0, 2).join('-')}
                                </Badge>
                            </div>

                            {/* Scores */}
                            <div className="mb-3 grid grid-cols-3 gap-2 text-xs">
                                <div className="flex items-center gap-1">
                                    <Shield className="h-3 w-3 text-red-500" />
                                    <span className="text-muted-foreground">Security:</span>
                                    <span className="font-medium">{(workflow.security_score * 100).toFixed(0)}%</span>
                                </div>
                                <div className="flex items-center gap-1">
                                    <Brain className="h-3 w-3 text-purple-500" />
                                    <span className="text-muted-foreground">AI:</span>
                                    <span className="font-medium">{(workflow.ai_score * 100).toFixed(0)}%</span>
                                </div>
                                <div className="flex items-center gap-1">
                                    <Zap className="h-3 w-3 text-blue-500" />
                                    <span className="text-muted-foreground">Auto:</span>
                                    <span className="font-medium">{(workflow.complexity_score * 100).toFixed(0)}%</span>
                                </div>
                            </div>

                            {/* Reason */}
                            <p className="mb-3 text-xs italic text-muted-foreground">
                                {workflow.reason}
                            </p>

                            {/* Integrations */}
                            {workflow.integrations.length > 0 && (
                                <div className="mb-3">
                                    <p className="mb-1 text-xs font-medium text-muted-foreground">
                                        Integrations:
                                    </p>
                                    <div className="flex flex-wrap gap-1">
                                        {workflow.integrations.slice(0, 3).map((integration) => (
                                            <Badge
                                                key={integration}
                                                variant="secondary"
                                                className="text-xs"
                                            >
                                                {integration.split('.').pop()}
                                            </Badge>
                                        ))}
                                        {workflow.integrations.length > 3 && (
                                            <Badge variant="secondary" className="text-xs">
                                                +{workflow.integrations.length - 3} more
                                            </Badge>
                                        )}
                                    </div>
                                </div>
                            )}

                            {/* Actions */}
                            <div className="flex gap-2">
                                <Button
                                    size="sm"
                                    className="flex-1"
                                    onClick={() => {
                                        // TODO: Implement workflow execution
                                        console.log('Execute workflow:', workflow.id);
                                    }}
                                >
                                    <Play className="mr-2 h-4 w-4" />
                                    Execute
                                </Button>
                                <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => {
                                        // TODO: Implement workflow preview
                                        console.log('View workflow:', workflow.id);
                                    }}
                                >
                                    View Details
                                </Button>
                            </div>
                        </div>
                    ))
                )}

                {/* Footer */}
                <div className="mt-4 rounded-lg border border-primary/20 bg-primary/5 p-3">
                    <p className="text-xs text-muted-foreground">
                        💡 <strong>Powered by {totalWorkflows.toLocaleString()} workflows</strong> across 6 repositories.
                        Recommendations are ranked by relevance, security focus, and AI capabilities.
                    </p>
                </div>
            </CardContent>
        </Card>
    );
}
