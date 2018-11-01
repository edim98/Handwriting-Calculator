LIBRARY IEEE;
USE IEEE.STD_LOGIC_1164.ALL;
USE IEEE.numeric_std.ALL;
USE IEEE.ALL;

ENTITY calculator IS
  PORT (
    	GPIO2 : IN STD_LOGIC; --header most significant bit
	GPIO3: 	IN STD_LOGIC; --header
	GPIO4: 	IN STD_LOGIC; --header
	GPIO5: 	IN STD_LOGIC; --header
	GPIO6: 	IN STD_LOGIC; --input1
	GPIO7: 	IN STD_LOGIC; --input2
	GPIO8: 	IN STD_LOGIC; --input3
	GPIO9: 	IN STD_LOGIC; --input4
	GPIO10: IN STD_LOGIC; --input5
	GPIO11: IN STD_LOGIC; --input6
	GPIO12: IN STD_LOGIC; --input7 least significant bit
	GPIO13: OUT STD_LOGIC;
	GPIO14: OUT STD_LOGIC;
	GPIO15: OUT STD_LOGIC;
	GPIO16: OUT STD_LOGIC;
	GPIO17: OUT STD_LOGIC;
	GPIO18: OUT STD_LOGIC;
	GPIO19: OUT STD_LOGIC;
	GPIO20: OUT STD_LOGIC;
	GPIO21: OUT STD_LOGIC;
	GPIO22: OUT STD_LOGIC;
	GPIO23: OUT STD_LOGIC;
	GPIO24: OUT STD_LOGIC;	
	GPIO25: OUT STD_LOGIC;
	GPIO26: OUT STD_LOGIC;
	GPIO27: OUT STD_LOGIC;
	led0 : OUT std_logic;
	led1 : OUT std_logic;
	led2 : OUT std_logic;
	led3 : OUT std_logic;
	led4 : OUT std_logic;
	led5 : OUT std_logic;
	led6 : OUT std_logic;
	led7 : OUT std_logic;
	led8 : OUT std_logic;
	led9 : OUT std_logic;
	HEX01 : OUT std_logic;
    	reset: 	IN std_logic;
    	clk: 	IN std_logic -- 50MHz clokc
    );
END calculator;

ARCHITECTURE calculate OF calculator IS
	signal test : INTEGER := 0;
 	SIGNAL result : std_logic_vector(11 downto 0):= "000000000000";
	SIGNAL numberold: signed(11 downto 0);
	SIGNAL headerback : std_logic_vector(2 downto 0);
	SIGNAL i : INTEGER := 0;
	SIGNAL numberoldadd: signed(11 downto 0);
	SIGNAL numberoldmultiply: signed(22 downto 0);
	signal numbertest : std_logic_vector(22 downto 0);
	SIGNAL numberolddivide: signed(11 downto 0);
	signal pi_clk: std_logic;
	SIGNAL c : INTEGER range 0 to 10000;
	signal count : integer := 2;
	
BEGIN
PROCESS (clk)ss
BEGIN
IF rising_edge(clk) THEN			--5 khz clock
	IF c < 5000 THEN
	c <= c + 1;
	pi_clk <= '0';
	ELSIF c = 5000 THEN
	pi_clk <= '1';
	c <= c + 1;
	ELSIF c > 5000 AND c < 10000 THEN
	c <= c + 1;
	ELSIF c = 10000 THEN
	c <= 0;
	pi_clk <= '0';
	END IF;
END IF;
END PROCESS;


PROCESS (pi_clk,reset)
	TYPE states IS(nothing, beginnow, add, multiply, divide, ready);
	VARIABLE state : states;
	VARIABLE header : std_logic_vector(3 downto 0); 
	VARIABLE number : signed(10 downto 0); 
	VARIABLE numberscount :  std_logic_vector(6 downto 0); 

BEGIN
	header := GPIO2 & GPIO3 & GPIO4 & GPIO5;
	number := GPIO2 & GPIO3 & GPIO4 & GPIO5 & GPIO6 & GPIO7 & GPIO8 & GPIO9 & GPIO10& GPIO11 & GPIO12;
	numberscount := GPIO6 & GPIO7 & GPIO8 & GPIO9 & GPIO10& GPIO11 & GPIO12;
	(GPIO16, GPIO17, GPIO18, GPIO19, GPIO20, GPIO21, GPIO22, GPIO23, GPIO24, GPIO25, GPIO26, GPIO27) <= result(11 downto 0);
	(GPIO13, GPIO14, GPIO15) <= headerback(2 downto 0);
	

IF reset = '0' THEN
	state := nothing;
	numberold <= "000000000000";
	numberoldmultiply <= "00000000000000000000001";
	numberoldadd <= "000000000000";
	numbertest <= "00000000000000000000001";
	led0 <= '0';
	led1 <= '0';
	led2 <= '0';
	led3 <= '0';
	led4 <= '0';
	led5 <= '0';
	led6 <= '0';
	led7 <= '0';
	led8 <= '0';
	led9 <= '0';
	GPIO13 <= '0';
	GPIO14 <= '0';
	GPIO15 <= '0';
	HEX01 <= '0';

ELSIF rising_edge(pi_clk) THEN
	led0 <= GPIO2;
	led1 <= GPIO3;
	led2 <= GPIO4;
	led3 <= GPIO5;
	led4 <= GPIO6;
	led5 <= GPIO7; 
	led6 <= GPIO8;
	led7 <= GPIO9;
	led8 <= GPIO10;
	led9 <= GPIO11;
	HEX01 <= GPIO12;
	
	CASE state IS
		WHEN nothing =>
			numberold <= "000000000000";
			numberoldadd <= "000000000000";
			numberoldmultiply <= "00000000000000000000001";
			numbertest <= "00000000000000000000001";
			i <= 0;
			IF header = "0001" THEN
				state := beginnow;
				headerback <= "010";
			ELSE 
				state := nothing;
				headerback <= "000";
			END IF;
		WHEN beginnow =>
			--count := to_integer(unsigned(numberscount));
			IF header = "0110" THEN
				state := add;		
				headerback <= "011";
			ELSIF header = "1000" THEN
				state := multiply;
				headerback <= "011";
			ELSIF header = "1001" THEN
				headerback <= "011";
				state := divide;
			ELSE 
				state := nothing;
				headerback <= "111";
			END IF;
		WHEN add => 
			IF i < count THEN
			numberoldadd <= numberoldadd(11 downto 0) + resize(signed(number), 11);
			i <= i + 1;
				IF headerback = "100" THEN
					headerback <= "101";	
				ELSIF headerback = "101" THEN
					headerback <= "100";
				ELSE
					headerback <= "100";
				END IF;				
			ELSIF i = count THEN
				state := ready;
				numberold <= numberoldadd(11 downto 0);
			--ELSIF numberoldadd(12) /= '1' THEN
				--state := nothing;
				--headerback <= "011";
				--numberoldadd <= "1000000000000";
			ELSE
				headerback <= "111";
				state := nothing;
			END IF;
		WHEN multiply =>
			IF i < count AND numbertest(22 downto 12) = "00000000000" THEN
			numberoldmultiply <= numberoldmultiply(11 downto 0) * signed(number);
			numbertest <= std_logic_vector((unsigned(numbertest(11 downto 0))) * to_unsigned(to_integer(abs(signed(number))), number'LENGTH));
			i <= i + 1;
				IF headerback = "100" THEN
					headerback <= "101";	
				ELSIF headerback = "101" THEN
					headerback <= "100";
				ELSE
					headerback <= "100";
				END IF;		
			ELSIF i = count AND numbertest(22 downto 12) = "00000000000" THEN
				numberold <= numberoldmultiply(11 downto 0);
				state := ready;
			ELSIF numbertest(22 downto 12) /= "00000000000" THEN
				state := nothing;
				headerback <= "011";
				numberoldmultiply <= "00000000000000000000001";
				numbertest <= "00000000000000000000001";
			ELSE
				headerback <= "111";
				state := nothing;
			END IF;
		WHEN divide =>
			IF i < count THEN
			numberolddivide <= numberolddivide / resize(signed(number),11);
			i <= i + 1;
				IF headerback = "100" THEN
					headerback <= "101";	
				ELSIF headerback = "101" THEN
					headerback <= "100";
				ELSE
					headerback <= "100";
				END IF;		
			ELSIF i = count THEN
				state := ready;
			ELSE
				headerback <= "111";
				state := nothing;
			END IF;
		WHEN ready =>
			result <= std_logic_vector(numberold);
			headerback <= "001";
			state := nothing;
		WHEN OTHERS => state:= nothing;
	END CASE;

END IF;
END PROCESS;
END calculate;

