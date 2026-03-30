/* eslint-disable @typescript-eslint/no-namespace */

declare global {
  namespace JSX {
    interface IntrinsicElements {
      'google-cast-launcher': any;
    }
  }
}

const CastButton = ({ ...props }) => {
  return <google-cast-launcher style={{ cursor: 'pointer' }} {...props} />;
};

CastButton.propTypes = {};

export default CastButton;
