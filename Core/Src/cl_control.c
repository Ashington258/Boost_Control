/* cl_control.c */
#include "cl_control.h"
/* 全局变量定义 */
float pi_error = 0.0f;
/**
 * @brief PI 控制器初始化
 */
void PI_Init(PI_Controller_t *pi, float kp, float ki, float output_limit)
{
    pi->kp = kp;
    pi->ki = ki;
    pi->integral = 0.0f;
    pi->output_limit = output_limit;
}

/**
 * @brief PI 迭代计算，含积分限幅与输出限幅
 */
float PI_Update(PI_Controller_t *pi, float target, float feedback, float dt)
{
    // UPdate 使用全局变量
    pi_error = -(target - feedback);

    // 更新积分项
    pi->integral += pi_error * dt;
    // 防止积分项过大，限幅在 [-output_limit/ki, +output_limit/ki]
    if (pi->ki > 0.0f)
    {
        float int_max = pi->output_limit / pi->ki;
        if (pi->integral > int_max)
            pi->integral = int_max;
        else if (pi->integral < -int_max)
            pi->integral = -int_max;
    }

    // PI 计算
    float output = pi->kp * pi_error + pi->ki * pi->integral;

    // 输出限幅
    if (output > pi->output_limit)
        output = pi->output_limit;
    else if (output < -pi->output_limit)
        output = -pi->output_limit;

    return output;
}

void PI_ResetIntegral(PI_Controller_t *pi)
{
    if (pi)
        pi->integral = 0.0f;
}