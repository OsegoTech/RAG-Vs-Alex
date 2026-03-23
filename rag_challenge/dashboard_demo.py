import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from metrics import MetricsCollector

def display_dashboard():
    print("=== RAG Performance Metrics Dashboard ===\n")

    metrics_collector = MetricsCollector()

    # Get metrics for last 7 days
    start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now()

    metrics_data = metrics_collector.get_metrics(start_date, end_date)
    summary_stats = metrics_collector.get_summary_stats(start_date, end_date)

    # Display summary
    print("📊 Key Performance Indicators:")
    print(f"   Total Queries: {summary_stats['total_queries']}")
    print(f"   Success Rate: {summary_stats['error_rate']*100:.1f}%")
    print(f"   Avg Response Time: {summary_stats['avg_response_time']:.2f}s")
    print(f"   Avg Documents Retrieved: {summary_stats['avg_documents_retrieved']:.1f}")
    print()

    if metrics_data:
        print("📈 Recent Queries:")
        for i, metric in enumerate(metrics_data[-5:], 1):  # Show last 5
            status = "✅" if metric['success'] else "❌"
            print(f"   {i}. {status} {metric['query'][:40]}... | {metric['response_time']:.2f}s | {metric['num_documents']} docs")
        print()

        # Simple trend analysis
        print("📉 Performance Trends:")
        if len(metrics_data) >= 2:
            recent = metrics_data[-3:]  # Last 3 queries
            avg_recent = sum(m['response_time'] for m in recent) / len(recent)
            older = metrics_data[:-3] if len(metrics_data) > 3 else []
            if older:
                avg_older = sum(m['response_time'] for m in older) / len(older)
                trend = "improving" if avg_recent < avg_older else "degrading"
                print(f"   Response time trend: {trend} ({avg_older:.2f}s → {avg_recent:.2f}s)")
            else:
                print(f"   Current avg response time: {avg_recent:.2f}s")
    else:
        print("No metrics data available. Run some queries first!")

if __name__ == "__main__":
    display_dashboard()