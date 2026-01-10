#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# S60 PID CONTROLLER: CONTROL ADAPTATIVO PARA SISTEMAS FLOQUET
# -------------------------------------------------------------------------------------
# Implementación de un controlador Proporcional-Integral-Derivativo (PID)
# utilizando aritmética pura Base-60 para estabilizar cristales de tiempo.
# -------------------------------------------------------------------------------------

from quantum.yatra_core import S60

class S60PID:
    """
    Controlador PID discreto para mantener variables de estado S60 estables.
    Ecuación: u(t) = Kp*e(t) + Ki*Integral(e) + Kd*Derivada(e)
    """
    def __init__(self, kp, ki, kd, setpoint=S60(0)):
        """
        :param kp: Ganancia Proporcional (S60)
        :param ki: Ganancia Integral (S60)
        :param kd: Ganancia Derivativa (S60)
        :param setpoint: Valor objetivo a mantener (S60)
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        
        # Estado interno
        self._prev_error = S60(0)
        self._integral = S60(0)
        
    def update(self, measured_value, dt):
        """
        Calcula la salida de control u(t) basada en el valor medido actual.
        :param measured_value: Valor actual del sistema (Input)
        :param dt: Paso de tiempo (S60)
        """
        # 1. Calcular Error
        error = self.setpoint - measured_value
        
        # 2. Término Proporcional
        p_term = self.kp * error
        
        # 3. Término Integral (Acumulación de error en el tiempo)
        # Integral += error * dt
        self._integral = self._integral + (error * dt)
        i_term = self.ki * self._integral
        
        # 4. Término Derivativo (Tasa de cambio del error)
        # Derivada = (error - prev_error) / dt
        if dt > S60(0):
            d_error = (error - self._prev_error) / dt
            d_term = self.kd * d_error
        else:
            d_term = S60(0)
            
        # Actualizar estado para siguiente ciclo
        self._prev_error = error
        
        # 5. Salida Total
        output = p_term + i_term + d_term
        
        return output

    def reset(self):
        """Reinicia la integral y el error previo."""
        self._prev_error = S60(0)
        self._integral = S60(0)

if __name__ == "__main__":
    # PRUEBA DE ESTABILIZACIÓN (UNIT TEST)
    print("🎛️  TESTING S60 PID CONTROLLER")
    
    # Objetivo: Mantener amplitud en 100
    target = S60(100)
    
    # Afinación (Gains) - Valores empíricos S60
    kp = S60(0, 30) # 0.5
    ki = S60(0, 5)  # 0.083
    kd = S60(0, 10) # 0.16
    
    pid = S60PID(kp, ki, kd, setpoint=target)
    
    current_val = S60(90) # Empezamos por debajo
    dt = S60(0, 1)        # 1 tick
    
    print(f"Target: {target} | Start: {current_val}")
    
    for i in range(5):
        output = pid.update(current_val, dt)
        print(f"Tick {i+1}: Input={current_val} -> PID Output (Fuerza)={output}")
        # Simulamos que el sistema responde subiendo
        current_val = current_val + (output * S60(0, 30)) # Aplica parte de la fuerza
        
    print(f"Final Value: {current_val}")
