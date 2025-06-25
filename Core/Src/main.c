/* USER CODE BEGIN Header */
/**
 ******************************************************************************
 * @file           : main.c
 * @brief          : Main program body
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2025 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "adc.h"
#include "dma.h"
#include "tim.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define CONTROL_PERIOD_S (0.001f) // 控制周期 1 ms
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
__attribute__((aligned(4))) uint16_t adc_buffer[2];

float v_adc = 0.0f;
float current = 0.0f;

float v_target = 36.00f;
float vadc_target = 0.0f;
float delta = 0.0f;
float base_duty = 0.0f;
float duty = 0.0f;

PI_Controller_t voltage_pi;
PIController v_pi;
/* 定义滤波器句柄 */
static IIR_LPF_HandleTypeDef lpf_vadc;
static IIR_LPF_HandleTypeDef lpf_current;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/**
 * @brief 电压拟合：根据vadc_target目标电压返回基础占空比
 */
static float BaseDuty_FromFit(float vadc_target)
{
  // 方法一：三次多项式拟合（更精确）
  float v2 = vadc_target * vadc_target;
  float v3 = v2 * vadc_target;
  return 100.0f * (-0.035971f * v3 + 0.355110f * v2 - 1.299556f * vadc_target + 2.059551f);

  // // 方法二：线性拟合（更高性能）
  // return 100.0f * (-0.221493f * vadc_target + 1.044567f);
}

/**
 * @brief 将输出电压转换为 ADC 目标电压（线性拟合）
 */
float calculate_vadc(float v_target)
{
  // 直接拟合@100Ohm Load
  // return 0.0743f * v_target - 0.0802f;

  // 电流补偿
  return 0.0743f * v_target - 1.0553 * current;
}

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
  if (htim->Instance == TIM2)
  {
    // ADC 原始采样
    float v_raw = adc_buffer[0] * 3.3f / 4096.0f;
    float i_raw = adc_buffer[1] * 3.3f / 4096.0f;

    // 滤波处理
    v_adc = IIR_LPF_Update(&lpf_vadc, v_raw);
    current = IIR_LPF_Update(&lpf_current, i_raw);

    // 不滤波
    //  v_adc = v_raw;
    //  current = i_raw;

    // PID 控制输出
    // delta = PI_Update(&voltage_pi, vadc_target, v_adc, CONTROL_PERIOD_S);
    delta = PIController_Update(&v_pi, vadc_target, v_adc);
    duty = base_duty + delta;

    // 限制输出占空比
    if (duty < 0.0f)
      duty = 0.0f;
    if (duty > 100.0f)
      duty = 100.0f;

    // 应用 PWM
    Set_PWM_Duty(&htim1, TIM_CHANNEL_1, duty);
  }
}

/* USER CODE END 0 */

/**
 * @brief  The application entry point.
 * @retval int
 */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_ADC1_Init();
  MX_TIM1_Init();
  MX_TIM2_Init();
  /* USER CODE BEGIN 2 */
  // PI_Init(&voltage_pi, 2.0f, 120.0f, 500.0f);
  PIController_Init(&v_pi, 10.0f, 300.0f, 0.001f, -50.0f, 50.0f); // kp, ki, dt(1ms), min, max
  vadc_target = calculate_vadc(v_target);
  base_duty = BaseDuty_FromFit(vadc_target);

  HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);
  Set_PWM_Duty(&htim1, TIM_CHANNEL_1, 45); // 初始占空比
  /* 首次读取 ADC，获得初始值 */
  HAL_ADC_Start_DMA(&hadc1, (uint32_t *)adc_buffer, 2);
  HAL_Delay(10); // 等待 DMA 首次采样完成
  float v_init = adc_buffer[0] * 3.3f / 4096.0f;
  float curr_init = adc_buffer[1] * 3.3f / 4096.0f;
  /* 初始化滤波器，α 推荐 0.6 */
  IIR_LPF_Init(&lpf_vadc, 0.9f, v_init);
  IIR_LPF_Init(&lpf_current, 0.90f, curr_init);

  HAL_TIM_Base_Start_IT(&htim2); // 启动中断模式定时器
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
 * @brief System Clock Configuration
 * @retval None
 */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
   */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
   * in the RCC_OscInitTypeDef structure.
   */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = 8;
  RCC_OscInitStruct.PLL.PLLN = 100;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 4;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
   */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_3) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
 * @brief  This function is executed in case of error occurrence.
 * @retval None
 */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef USE_FULL_ASSERT
/**
 * @brief  Reports the name of the source file and the source line number
 *         where the assert_param error has occurred.
 * @param  file: pointer to the source file name
 * @param  line: assert_param error line source number
 * @retval None
 */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  // printf("Wrong parameters value: file %s on line %d\r\n", file, line);
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */