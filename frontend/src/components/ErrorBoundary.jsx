import { Component } from "react";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught:", error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <div className="error-boundary-card glass-card">
            <div className="error-boundary-icon">⚠️</div>
            <h2>Something went wrong</h2>
            <p className="error-boundary-message">
              An unexpected error occurred. Please try again.
            </p>
            {this.state.error && (
              <details className="error-boundary-details">
                <summary>Technical Details</summary>
                <code>{this.state.error.toString()}</code>
              </details>
            )}
            <div className="error-boundary-actions">
              <button className="submit-btn" onClick={this.handleReset}>
                Try Again
              </button>
              <button
                className="analyze-another-btn"
                onClick={() => window.location.reload()}
              >
                Reload Page
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
