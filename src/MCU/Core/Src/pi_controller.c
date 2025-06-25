#include "pi_controller.h"
float error;

void PIController_Init(PIController *ctrl, float kp, float ki, float dt, float out_min, float out_max)
{
    ctrl->kp = kp;
    ctrl->ki = ki;
    ctrl->dt = dt;
    ctrl->integral = 0.0f;
    ctrl->output_min = out_min;
    ctrl->output_max = out_max;
}

float PIController_Update(PIController *ctrl, float setpoint, float measurement)
{
    error = -(setpoint - measurement);

    // 积分项更新
    ctrl->integral += error * ctrl->dt;

    // PI输出计算
    float output = ctrl->kp * error + ctrl->ki * ctrl->integral;

    // 限制输出 & 防止积分饱和
    if (output > ctrl->output_max)
    {
        output = ctrl->output_max;
        ctrl->integral -= error * ctrl->dt; // 抑制积分项继续增长
    }
    else if (output < ctrl->output_min)
    {
        output = ctrl->output_min;
        ctrl->integral -= error * ctrl->dt;
    }

    return output;
}
