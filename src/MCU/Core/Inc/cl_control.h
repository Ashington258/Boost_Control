/* cl_control.h */
#ifndef __CL_CONTROL_H
#define __CL_CONTROL_H

#include <stdint.h>

typedef struct
{
    float kp;           // 比例系数
    float ki;           // 积分系数
    float integral;     // 积分项累加
    float output_limit; // 输出（duty）最大绝对值
} PI_Controller_t;

/**
 * @brief   初始化 PI 控制器
 * @param   pi            控制器对象
 * @param   kp            比例系数
 * @param   ki            积分系数
 * @param   output_limit  输出限幅（正负最大占空比）
 */
void PI_Init(PI_Controller_t *pi, float kp, float ki, float output_limit);

/**
 * @brief   执行一次 PI 计算
 * @param   pi         控制器对象
 * @param   target     目标值（Setpoint）
 * @param   feedback   测量值（Process variable）
 * @param   dt         采样时间(s)
 * @retval  计算后输出（如 PWM 占空比）
 */
float PI_Update(PI_Controller_t *pi, float target, float feedback, float dt);

void PI_ResetIntegral(PI_Controller_t *pi);

/* === 调试用全局变量 === */
extern float pi_error;
#endif /* __CL_CONTROL_H */
