import React from 'react';

/** Falls back to the lightweight infographic if the WebGL scene throws while rendering. */
class SceneErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { failed: false };
  }

  static getDerivedStateFromError() {
    return { failed: true };
  }

  componentDidCatch(error) {
    console.error('3D scene failed, showing the lightweight version instead:', error);
    if (this.props.onError) this.props.onError(error);
  }

  render() {
    return this.state.failed ? this.props.fallback : this.props.children;
  }
}

export default SceneErrorBoundary;
