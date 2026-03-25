export const Button = ({ children, variant = 'primary', fullWidth, isLoading, style, ...props }) => {
  const isPrimary = variant === 'primary';
  
  return (
    <button
      disabled={isLoading || props.disabled}
      style={{
        padding: '10px 18px',
        backgroundColor: isPrimary ? 'var(--accent-primary)' : 'transparent',
        color: isPrimary ? '#FFFFFF' : 'var(--text-primary)',
        border: isPrimary ? 'none' : '1px solid var(--border-color)',
        borderRadius: '6px',
        fontSize: '15px',
        fontWeight: 500,
        cursor: (isLoading || props.disabled) ? 'not-allowed' : 'pointer',
        width: fullWidth ? '100%' : 'auto',
        transition: 'background-color 0.2s, transform 0.1s',
        opacity: (isLoading || props.disabled) ? 0.7 : 1,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        gap: '8px',
        ...style
      }}
      onMouseEnter={(e) => {
        if (!isLoading && !props.disabled) {
          e.target.style.backgroundColor = isPrimary ? 'var(--accent-hover)' : 'var(--bg-secondary)';
        }
      }}
      onMouseLeave={(e) => {
        if (!isLoading && !props.disabled) {
          e.target.style.backgroundColor = isPrimary ? 'var(--accent-primary)' : 'transparent';
        }
      }}
      onMouseDown={(e) => {
        if (!isLoading && !props.disabled) e.target.style.transform = 'scale(0.98)';
      }}
      onMouseUp={(e) => {
        if (!isLoading && !props.disabled) e.target.style.transform = 'scale(1)';
      }}
      {...props}
    >
      {isLoading ? 'Processing...' : children}
    </button>
  );
};
