import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve


# Boost 占空比非线性方程
def boost_duty_equation(D, Vout, Vin, R, RL):
    if D <= 0 or D >= 1:
        return 1e6  # 防止非法值
    one_minus_D = 1 - D
    left = Vout / Vin
    right = (1 / one_minus_D) / (1 + (1 / one_minus_D**2) * (RL / R))
    return left - right


# 求解 D 的函数
def solve_boost_duty(Vout, Vin, R, RL, D_guess=0.5):
    solution = fsolve(boost_duty_equation, D_guess, args=(Vout, Vin, R, RL))
    D = solution[0]
    return D if 0 < D < 1 else np.nan  # 限制在合理范围


# 固定参数
Vout = 36.0  # 输出电压
Vin = 18.0  # 输入电压
R = 0.2  # 电源等效串联电阻

# 扫描负载电阻
RL_values = np.linspace(1, 500, 300)
D_values = [solve_boost_duty(Vout, Vin, R, RL) for RL in RL_values]

# 绘图
plt.figure(figsize=(10, 6))
plt.plot(RL_values, D_values, label="Boost 占空比 D vs 负载电阻", color="blue")
plt.xlabel("负载电阻 R_L (Ohm)")
plt.ylabel("占空比 D")
plt.title("Boost 占空比 D 随负载电阻变化曲线\n(Vout=36V, Vin=18V, R=1Ω)")
plt.grid(True)
plt.ylim(0, 1)
plt.legend()
plt.tight_layout()
plt.show()
