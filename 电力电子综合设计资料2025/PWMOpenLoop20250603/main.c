
//******************WTU SEEE WWB PWM20250603****************************//

#include<reg52.h>
#include<intrins.h>
#define uint unsigned int
#define uchar unsigned char
 
sbit PWM=P2^1;//P2.1输出pwm
sbit CS=P2^3; //AD采样使能
sbit CLK=P2^2;//时钟
sbit DIDO=P2^0;//DIDO输出
sbit PWMCON=P2^4;//驱动使能

uchar flag,DutyCycle;  // 定义占空比的变化
uint TH01,TL01,TH02,TL02,FrequencyKhz;
uint temp,dat2;
uint vvv,i,m;

unsigned char code tab[] = {0xc0, 0xf9, 0xa4, 0xb0, 0x99, 0x92, 0x82, 0xf8, 0x80, 0x90};
uchar code tab1[]={0x40,0x79,0x24,0x30,0x19,0x12,0x02,0x78,0x00,0x10};
	

void PWMCal(uchar DutyCycle, uint FrequencyKhz)// 0~100%  kHz
{
	if (DutyCycle>=100)
		 DutyCycle=100;
	else if (DutyCycle<0)
	   DutyCycle=0;


	TH01=(65536-(uint)(0.9216*DutyCycle*10)/FrequencyKhz)/256;
	TL01=(65536-(uint)(0.9216*DutyCycle*10)/FrequencyKhz)%256;
	TH02=(65536-(uint)(0.9216*(100-DutyCycle)*10)/FrequencyKhz)/256;
	TL02=(65536-(uint)(0.9216*(100-DutyCycle)*10)/FrequencyKhz)%256;
	

	TR0=1;//启动定时器0 
}


void delay(int tt)//1ms
		{
		while(tt--)
		  {for(i=0;i<120;i++);}
}
		
//**********************AD Sampling channel choice*******************************//
uchar choiceADC(uint CH)//CH为0选择通道ch0，为1，选择ch1进行AD转换
	{
		uchar dat;
		CS=1;
		_nop_();
		CLK=1;
		CS=0;			 
		DIDO = 1;CLK = 0;_nop_();CLK = 1;_nop_();  //first clk
		DIDO = 1;CLK = 0;_nop_();CLK = 1;_nop_(); //second clk
		DIDO = CH;CLK = 0;_nop_();CLK = 1;_nop_(); //channel
		DIDO = 1;                       
	for(i = 0;i < 8;i++)
	{
		CLK = 0;_nop_();
		if(DIDO)dat |= 0x01;
		CLK = 1;_nop_();
		dat = dat <<= 1;
	}
   return(dat);
   CS = 1;			 
				 
	}

	
	  //**********************ShuMaGuan show*******************************//
void display(uint dat1)
		{
	

		dat1=(dat1*100.0*5*11)/255.0;
	
	  P3=0xfe;
		P0=tab[dat1/1000];
		delay(1);
		P0=0xff;
			
	  P3=0xfd;
		P0=tab1[dat1%1000/100];
		delay(1);
		P0=0xff;
			
		P3=0xfb;
		P0=tab[dat1%100/10];
		delay(1);
		P0=0xff;
			
		P3=0xf7;
		P0=tab[dat1%10];
		delay(1);
		P0=0xff;
			
		}
		
		
void main()// (65536-X)*12/11.0592=Expected one  
{
	
	TMOD=0x01;//定时器0工作方式1
	EA=1;//开总中断
	ET0=1;//开定时器0中断
	//PWMCal(70,20);//第1个数据为占空比1-70%，第2个数据理论上为开关频率20kHz， 实际测试时12.5kHz 51系列有误差
	PWMCal(70,40);//第1个数据为占空比1-70%，第2个数据理论上为开关频率40kHz，实测为17.9kHz开关频率,51系列对高频PWM有误差
	P3=0xFF;
	P0=0xFF;
	PWMCON=1;//驱动使能
	
	while(1)
	{			
			   vvv=choiceADC(0);//只做电压的检测部分检测。
		
		    // dat2=(vvv*100.0*5*11)/255.0;
		      dat2=0;//test  正常接入保护时，需要用上面一条代码,此语句强制输出PWM
		     
		     if(dat2>=4000)//保护作用，当输出电压超过40V，将占空比为0。
				   {
				   	PWMCal(0,20);	 //100%占空比，20khz  
			     }
				 
					for (m=0;m<=20;m++)//数码管显示
		       {
						 display(vvv);
						 delay(5); 
					 }
			}			
}
 
void tim0() interrupt 1
{
	if (flag)
	{
		TH0=TH01;
		TL0=TL01;
		PWM=1;
		flag=0;
		}
	
	else
	{
		TH0=TH02;
		TL0=TL02;
		PWM=0;
		flag=1;

	}

}

//******************WTU SEEE  WWB  PWM202506 END****************************//
