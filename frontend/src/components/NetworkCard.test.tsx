import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { NetworkCard, NetworkInfo } from './NetworkCard';
import { ClientNetworkInfo } from '@/hooks/useNetworkInfo';

// Mock MiniChart as it uses SVG and might be complex to test here
vi.mock('./MiniChart', () => ({
  MiniChart: () => <div data-testid="mini-chart">MiniChart</div>,
}));

describe('NetworkCard', () => {
  const mockNetwork: NetworkInfo = {
    net_bytes_sent: 1024 * 1024 * 5, // 5 MB
    net_bytes_recv: 1024 * 1024 * 10, // 10 MB
    net_packets_sent: 5000,
    net_packets_recv: 8000,
    wifi: {
      ssid: 'Server-WiFi',
      signal: 80,
      connected: true,
    },
  };

  const mockClientNetwork: ClientNetworkInfo = {
    wifi: {
      ssid: 'Client-WiFi',
      signal: 60,
      connected: true,
    },
  };

  it('renders "Sin datos de red" when no data is provided', () => {
    render(<NetworkCard />);
    expect(screen.getByText('Sin datos de red')).toBeInTheDocument();
  });

  it('renders network statistics correctly', () => {
    render(<NetworkCard network={mockNetwork} />);

    expect(screen.getByText('Red')).toBeInTheDocument();
    expect(screen.getByText('5.0 MB')).toBeInTheDocument();
    expect(screen.getByText('10 MB')).toBeInTheDocument(); // 10 >= 10, so 0 decimal places
    expect(screen.getByText('5.0k')).toBeInTheDocument();
    expect(screen.getByText('8.0k')).toBeInTheDocument();
    expect(screen.getByText('0.0 GB')).toBeInTheDocument(); // 15MB is 0.0 GB
  });

  it('prefers client WiFi over server WiFi', () => {
    render(<NetworkCard network={mockNetwork} clientNetwork={mockClientNetwork} />);

    expect(screen.getByText('WiFi del navegador')).toBeInTheDocument();
    expect(screen.getByText('Bueno')).toBeInTheDocument(); // 60% is "Bueno"
    expect(screen.getByText('60%')).toBeInTheDocument();
  });

  it('falls back to server WiFi if client WiFi is not connected', () => {
    const disconnectedClient: ClientNetworkInfo = {
      wifi: { connected: false },
    };
    render(<NetworkCard network={mockNetwork} clientNetwork={disconnectedClient} />);

    expect(screen.getByText('WiFi del servidor')).toBeInTheDocument();
    expect(screen.getByText('Excelente')).toBeInTheDocument(); // 80% is "Excelente"
    expect(screen.getByText('80%')).toBeInTheDocument();
  });

  it('shows disconnected state for WiFi', () => {
    const disconnectedNetwork: NetworkInfo = {
      ...mockNetwork,
      wifi: { ssid: 'Server-WiFi', signal: 0, connected: false }
    };
    render(<NetworkCard network={disconnectedNetwork} />);

    expect(screen.getByText('Desconectado')).toBeInTheDocument();
  });

  it('renders signal colors correctly based on signal strength', () => {
    const testSignals = [
      { signal: 80, expected: 'Excelente' },
      { signal: 60, expected: 'Bueno' },
      { signal: 40, expected: 'Moderado' },
      { signal: 10, expected: 'Débil' },
    ];

    testSignals.forEach(({ signal, expected }) => {
      const { unmount } = render(
        <NetworkCard network={{ ...mockNetwork, wifi: { ssid: 'Test', signal, connected: true } }} />
      );
      expect(screen.getByText(expected)).toBeInTheDocument();
      unmount();
    });
  });

  it('renders history chart when history data is provided', () => {
    const history = [
      { timestamp: 1, value: 10 },
      { timestamp: 2, value: 20 },
    ];
    render(<NetworkCard network={mockNetwork} history={history} />);
    expect(screen.getByTestId('mini-chart')).toBeInTheDocument();
  });
});
