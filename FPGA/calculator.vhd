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
	dig0, dig1, dig2, dig3, dig4 : OUT std_logic_vector(6 DOWNTO 0);
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
	signal error : std_logic;

	-- Binary to BCD
	signal negative : std_logic;
	signal ones : unsigned (3 downto 0);
	signal tens : unsigned(3 downto 0);
	signal hundreds: unsigned(3 downto 0);
	signal thousands: unsigned(3 downto 0);
	signal shift : integer := 0;
	signal shifting : std_logic;
	SIGNAL shiftresult : std_logic_vector(11 downto 0);
	signal postivenumber : std_logic_vector(11 downto 0);
	
	FUNCTION hex2display (n:std_logic_vector(3 DOWNTO 0)) RETURN std_logic_vector IS
	VARIABLE res : std_logic_vector(6 DOWNTO 0);
		BEGIN
		CASE n IS -- gfedcba; low active
			WHEN "0000" => RETURN NOT "0111111";
			WHEN "0001" => RETURN NOT "0000110";
			WHEN "0010" => RETURN NOT "1011011";
			WHEN "0011" => RETURN NOT "1001111";
			WHEN "0100" => RETURN NOT "1100110";
			WHEN "0101" => RETURN NOT "1101101";
			WHEN "0110" => RETURN NOT "1111101";
			WHEN "0111" => RETURN NOT "0000111";
			WHEN "1000" => RETURN NOT "1111111";
			WHEN "1001" => RETURN NOT "1101111";
			WHEN "1010" => RETURN NOT "1110111";
			WHEN "1011" => RETURN NOT "1111100";
			WHEN "1100" => RETURN NOT "0111001";
			WHEN "1101" => RETURN NOT "1011110";
			WHEN "1110" => RETURN NOT "1111001";
			WHEN OTHERS => RETURN NOT "1110001";
		END CASE;
	END hex2display;
	

BEGIN
PROCESS (clk)
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
	shifting <= '0';
	error <= '0';

ELSIF rising_edge(pi_clk) THEN
		
	CASE state IS
		WHEN nothing =>
			shifting <= '0';
			numberold <= "000000000000";
			numberoldadd <= "000000000000";
			numberoldmultiply <= "00000000000000000000001";
			numbertest <= "00000000000000000000001";
			i <= 0;
			IF header = "0001" THEN
				state := beginnow;
				headerback <= "010";
			ELSIF header = "1111" THEN
				state := nothing;
				error <= '1';
			ELSE 
				state := nothing;
				headerback <= "000";
			END IF;
		WHEN beginnow =>
			error <= '0';
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
				error <= '1';
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
				error <= '1';
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
				error <= '1';
			ELSE
				headerback <= "111";
				error <= '1';
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
				error <= '1';
				state := nothing;
			END IF;
		WHEN ready =>
			result <= std_logic_vector(numberold);
			headerback <= "001";
			state := nothing;
			--BCD
			shifting <= '1';
			postivenumber <= std_logic_vector(to_unsigned(to_integer(abs(signed(numberold))),result'LENGTH));
		WHEN OTHERS => state:= nothing;
	END CASE;
END IF;
END PROCESS;
PROCESS(clk)

BEGIN
IF reset = '0' THEN
		dig4 <= NOT "0000000";
		dig3 <= NOT "0111111";
		dig2 <= NOT "0111111";
		dig1 <= NOT "0111111";
		dig0 <= NOT "0111111";
ELSIF rising_edge(clk) THEN
		--Binary to BCD conversion

		IF shift = 0 and shifting = '1' THEN	
			shiftresult(11 downto 0) <= std_logic_vector(shift_left(unsigned(postivenumber), 1));
			ones(0) <= postivenumber(11);
			ones(3 downto 1) <= "000";
			tens <= "0000";
			hundreds <= "0000";
			thousands <= "0000";
			shift <= 1;
			IF result(11) = '0' THEN
				negative <= '0';
			ELSIF result(11) = '1' THEN
				negative <= '1';
			END IF;
		ELSIF shift /= 0 and shift < 12 and shifting = '1' THEN
			-- Ones
			shiftresult(11 downto 0) <= std_logic_vector(shift_left(unsigned(shiftresult),1));
			IF shiftresult(11) = '1' AND ones >= 5 THEN
				ones <= "0001" + shift_left(ones + 3, 1);
			ELSIF shiftresult(11) = '1' AND ones < 5 THEN
				ones <= "0001" + shift_left(ones, 1);
			ELSIF shiftresult(11) = '0' AND ones >= 5 THEN
				ones <= shift_left(ones + 3, 1);
			ELSIF shiftresult(11) = '0' AND ones < 5 THEN
				ones <= shift_left(ones, 1);
			END IF;
			-- Tens
			IF (ones(3) = '1' or ones >= 5) AND tens >= 5 THEN
				tens <= "0001" + shift_left(tens + 3, 1);
			ELSIF (ones(3) = '1' or ones >= 5) AND tens < 5 THEN
				tens <= "0001" + shift_left(tens, 1);
			ELSIF ones(3) = '0' AND ones < 5 AND tens >= 5 THEN
				tens <= shift_left(tens + 3, 1);
			ELSIF ones(3) = '0' AND ones < 5 AND tens < 5 THEN
				tens <= shift_left(tens, 1);
			END IF;
			-- Hundreds
			IF (tens(3) = '1' or tens >= 5) AND hundreds >= 5 THEN					--The addition of 3 will not create problems because the fourth 
				hundreds <= "0001" + shift_left(hundreds + 3, 1);
			ELSIF (tens(3) = '1' or tens >= 5) AND hundreds < 5 THEN
				hundreds <= "0001" + shift_left(hundreds, 1);
			ELSIF tens(3) = '0' AND tens < 5 AND hundreds >= 5 THEN
				hundreds <= shift_left(hundreds + 3, 1);
			ELSIF tens(3) = '0' AND tens < 5 AND hundreds < 5 THEN
				hundreds <= shift_left(hundreds, 1);
			END IF;
			--Thousands
			IF (hundreds(3) = '1' or hundreds >= 5) AND thousands >= 5 THEN					
				thousands <= "0001" + shift_left(thousands + 3, 1);
			ELSIF (hundreds(3) = '1' or hundreds >= 5) AND thousands < 5 THEN
				thousands <= "0001" + shift_left(thousands, 1);
			ELSIF hundreds(3) = '0' AND hundreds < 5 AND thousands >= 5 THEN
				thousands <= shift_left(thousands + 3, 1);
			ELSIF hundreds(3) = '0' AND hundreds < 5 AND thousands < 5 THEN
				thousands <= shift_left(thousands, 1);
			END IF;
			shift <= shift + 1;
		END if;

		IF shift = 12 and shifting = '1' THEN
			dig3 <= hex2display(std_logic_vector(thousands));
			dig2 <= hex2display(std_logic_vector(hundreds));
			dig1 <= hex2display(std_logic_vector(tens));
			dig0 <= hex2display(std_logic_vector(ones));
			IF negative = '1' THEN
			dig4 <= NOT "1000000";
			ELSIF negative = '0' THEN
			dig4 <= NOT "0000000";
			END IF;
		shift <= 0;
		END IF;

		IF error = '1' THEN
			dig0 <= NOT "1010000";
			dig1 <= NOT "1011100";
			dig2 <= NOT "1010000";
			dig3 <= NOT "1010000";
			dig4 <= NOT "1111001";
		END IF;
			
END IF;
END PROCESS;
END calculate;