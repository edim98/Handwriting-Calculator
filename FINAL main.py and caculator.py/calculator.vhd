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
	dig0, dig1, dig2, dig3, dig4, dig5 : OUT std_logic_vector(6 DOWNTO 0);
    	reset: 	IN std_logic;
    	clk: 	IN std_logic -- 50MHz clokc
    );
END calculator;

ARCHITECTURE calculate OF calculator IS
	signal test : INTEGER := 0;
 	SIGNAL result : std_logic_vector(11 downto 0);
	SIGNAL numberold: signed(59 downto 0);
	SIGNAL headerback : std_logic_vector(2 downto 0);
	SIGNAL i : INTEGER := 0;
	SIGNAL numberoldadd: signed(59 downto 0);
	SIGNAL numberoldmultiply: signed(115 downto 0);
	SIGNAL numberoldmultiplytemp: signed(115 downto 0);
	signal numbertest : std_logic_vector(115 downto 0);
	signal numbertesttemp : std_logic_vector(115 downto 0);
	SIGNAL numberolddivide: signed(59 downto 0);
	SIGNAL numbercomplete: signed(55 downto 0);
	signal pi_clk: std_logic;
	SIGNAL c : INTEGER range 0 to 20000;
	signal count : integer := 2;
	signal error : std_logic;
	signal perror : std_logic;
	signal n : integer range 0 to 49;	
	signal calculate : std_logic;
	signal headerswitch : std_logic;
	signal r : INTEGER range 0 to 49;

	-- Binary to BCD
	signal negative : std_logic;
	signal ones : unsigned (3 downto 0);
	signal tens : unsigned(3 downto 0);
	signal hundreds: unsigned(3 downto 0);
	signal thousands: unsigned(3 downto 0);
	signal tenthousands: unsigned(3 downto 0);
	signal shift : integer := 0;
	signal shifting : std_logic;
	SIGNAL shiftresult : std_logic_vector(59 downto 0);
	signal postivenumber : std_logic_vector(59 downto 0);
	
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

	procedure multiplication(
	numbercomplete : in signed(55 downto 0);
	numberoldmultiply : in signed(115 downto 0);
	SIGNAL numberoldmultiplytemp: out signed(115 downto 0)) is
	BEGIN
		numberoldmultiplytemp <= numberoldmultiply(59 downto 0) * signed(numbercomplete);
	end multiplication;

	procedure multiplicationtest(
	numbercomplete : in signed(55 downto 0);
	numbertest : in std_logic_vector(115 downto 0);
	signal numbertesttemp : out std_logic_vector(115 downto 0)) is
	BEGIN
		numbertesttemp <= std_logic_vector((unsigned(numbertest(59 downto 0))) * to_unsigned(to_integer(abs(signed(numbercomplete))), numbercomplete'LENGTH));
	end multiplicationtest;
	

BEGIN
PROCESS (clk)
BEGIN
IF rising_edge(clk) THEN			--5 khz clock
	IF c < 10000 THEN
	c <= c + 1;
	pi_clk <= '0';
	ELSIF c = 10000 THEN
	pi_clk <= '1';
	c <= c + 1;
	ELSIF c > 10000 AND c < 20000 THEN
	c <= c + 1;
	ELSIF c = 20000 THEN
	c <= 0;
	pi_clk <= '0';
	END IF;
END IF;
END PROCESS;


PROCESS (pi_clk,reset)
	TYPE states IS(nothing, beginnow, add, multiply, divide, ready);
	VARIABLE state : states;
	VARIABLE header : std_logic_vector(3 downto 0); 
	VARIABLE number : signed(6 downto 0); 

BEGIN
	header := GPIO2 & GPIO3 & GPIO4 & GPIO5;
	-- number := GPIO2 & GPIO3 & GPIO4 & GPIO5 & GPIO6 & GPIO7 & GPIO8 & GPIO9 & GPIO10& GPIO11 & GPIO12;
	number := GPIO6 & GPIO7 & GPIO8 & GPIO9 & GPIO10& GPIO11 & GPIO12;
	(GPIO16, GPIO17, GPIO18, GPIO19, GPIO20, GPIO21, GPIO22, GPIO23, GPIO24, GPIO25, GPIO26, GPIO27) <= result(11 downto 0);
	(GPIO13, GPIO14, GPIO15) <= headerback(2 downto 0);
	

IF reset = '0' THEN
	state := nothing;
	numberold <= (others => '0');
	numberoldadd <= (others => '0');
	numberoldmultiply(115 downto 1) <= (others => '0');
	numberoldmultiply(0) <= '1';
	numbertest(115 downto 1) <=  (others => '0');
	numbertest(0) <= '1';
	numberoldmultiplytemp(115 downto 1) <= (others => '0');
	numberoldmultiplytemp(0) <= '1';
	numbertesttemp(115 downto 1) <=  (others => '0');
	numbertesttemp(0) <= '1';
	shifting <= '0';
	error <= '0';
	perror <= '0';
	headerswitch <= '0';
	n <= 0;
	r <= 0;
	calculate <= '0';
	negative <= '0';

ELSIF rising_edge(pi_clk) THEN
		
	CASE state IS
		WHEN nothing =>
			headerback <= "000";
			numberold <= (others => '0');
			numberoldadd <= (others => '0');
			numberoldmultiply(115 downto 1) <= (others => '0');
			numberoldmultiply(0) <= '1';
			numbertest(115 downto 1) <=  (others => '0');
			numbertest(0) <= '1';
			numbertesttemp(115 downto 1) <=  (others => '0');
			numbertesttemp(0) <= '1';
			numberoldmultiplytemp(115 downto 1) <= (others => '0');
			numberoldmultiplytemp(0) <= '1';
			i <= 0;
			n <= 0;
			r <= 0;
			IF header = "0001" THEN
				state := beginnow;
				shifting <= '0';
				headerback <= "010";
			ELSIF header = "1111" THEN
				state := nothing;
				perror <= '1';
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
			ELSIF header = "1111" THEN
				state := nothing;
				perror <= '1';
			ELSE 
				state := nothing;
				error <= '1';
				headerback <= "111";
			END IF;
		WHEN add => 
			IF headerswitch = '0' AND i /= count AND calculate = '0' THEN
				IF (n = 0 OR n = 14 OR n = 28 OR n = 42) AND header = "0100" THEN	
					numbercomplete(55-n downto 49-n) <= number;
					n <= n + 7;
					headerswitch <= '1';
					IF headerback = "100" THEN
						headerback <= "101";	
					ELSIF headerback = "101" THEN
						headerback <= "100";
					ELSE
						headerback <= "100";
					END IF;
				ELSIF (n = 0 OR n = 14 OR n = 28 OR n = 42) AND header = "0101" THEN
					state := add;
				ELSE 
					calculate <= '0';
					headerback <= "111";
					error <= '1';
					state := nothing;
				END IF;
				
			ELSIF headerswitch = '1' AND i /= count AND calculate = '0' THEN
				IF (n = 7 OR n = 21 OR n = 35) AND header = "0101" THEN
					numbercomplete(55-n downto 49-n) <= number;
					n <= n + 7;
					headerswitch <= '0';
					IF headerback = "100" THEN
						headerback <= "101";	
					ELSIF headerback = "101" THEN
						headerback <= "100";
					ELSE
						headerback <= "100";
					END IF;
				ELSIF n = 49 and header = "0101" THEN
					numbercomplete(6 downto 0) <= number;
					n <= 0;
					headerback <= "101";
					calculate <= '1';
					headerswitch <= '0';
				ELSIF (n = 7 OR n = 21 OR n = 35 OR n = 49) AND header = "0100" THEN
					state := add;
				ELSE 
					calculate <= '0';
					headerback <= "111";
					error <= '1';
					state := nothing;
				END IF;
			END IF;
	
			IF i < count AND calculate = '1' THEN
				numberoldadd <= numberoldadd(59 downto 0) + resize(signed(numbercomplete), 60);
				i <= i + 1;
				calculate <= '0';			
			ELSIF i = count THEN
				state := ready;
				numberold <= numberoldadd(59 downto 0);
				i <= 0;			
			END IF;
			
			IF header = "1111" THEN
				state := nothing;
				perror <= '1';
			END IF;
			
		WHEN multiply =>
			numberoldmultiply <= numberoldmultiplytemp;
			numbertest <= numbertesttemp;
			IF headerswitch = '0' AND i /= count AND calculate = '0' THEN
				IF (n = 0 OR n = 14 OR n = 28 OR n = 42) AND header = "0100" THEN	
					numbercomplete((55-n) downto (49-n)) <= number;
					n <= n + 7;
					headerswitch <= '1';
					IF headerback = "100" THEN
						headerback <= "101";	
					ELSIF headerback = "101" THEN
						headerback <= "100";
					ELSE
						headerback <= "100";
					END IF;
				ELSIF (n = 0 OR n = 14 OR n = 28 OR n = 42) AND header = "0101" THEN
					state := multiply;
				ELSE 
					calculate <= '0';
					headerback <= "111";
					error <= '1';
					state := nothing;
				END IF;
			ELSIF headerswitch = '1' AND i /= count AND calculate = '0' THEN
				IF (n = 7 OR n = 21 OR n = 35) AND header = "0101" THEN
					numbercomplete((55-n) downto (49-n)) <= number;
					n <= n + 7;
					headerswitch <= '0';
					IF headerback = "100" THEN
						headerback <= "101";	
					ELSIF headerback = "101" THEN
						headerback <= "100";
					ELSE
						headerback <= "100";
					END IF;
				ELSIF n = 49 and header = "0101" THEN
					numbercomplete(6 downto 0) <= number;
					n <= 0;
					calculate <= '1';
					headerswitch <= '0';
					headerback <= "101";
				ELSIF (n = 7 OR n = 21 OR n = 35 OR n = 49) AND header = "0100" THEN
					state := multiply;
				ELSE
					calculate <= '0';
					headerback <= "111";
					error <= '1';
					state := nothing;	
				END IF;
			END IF;

			IF i < count AND numbertesttemp(115 downto 55) = "0000000000000000000000000000000000000000000000000000000000000" AND calculate = '1' THEN
				multiplication(numbercomplete, numberoldmultiply, numberoldmultiplytemp);
				multiplicationtest(numbercomplete, numbertest, numbertesttemp);
				i <= i + 1;
				calculate <= '0';
					
			ELSIF i = count AND numbertesttemp(115 downto 55) = "0000000000000000000000000000000000000000000000000000000000000" THEN
				numberold <= numberoldmultiplytemp(59 downto 0);
				i <= 0;
				state := ready;
			ELSIF numbertesttemp(115 downto 55) /= "0000000000000000000000000000000000000000000000000000000000000" THEN
				state := nothing;
				headerback <= "110";
				numberoldmultiplytemp(115 downto 1) <= (others => '0');
				numberoldmultiplytemp(0) <= '1';
				numberoldmultiply(115 downto 1) <= (others => '0');
				numberoldmultiply(0) <= '1';
				numbertesttemp(115 downto 1) <=  (others => '0');
				numbertesttemp(0) <= '1';
				numbertest(115 downto 1) <=  (others => '0');
				numbertest(0) <= '1';
				error <= '1';
			END IF;
			
			IF header = "1111" THEN
				state := nothing;
				perror <= '1';
			END IF;
			
		WHEN divide =>
			IF headerswitch = '0' AND i /= count AND calculate = '0' THEN
				IF n < 49 AND header = "0100" THEN	
					numbercomplete((55-n) downto (49-n)) <= number;
					n <= n + 7;
					headerswitch <= '1';
					IF headerback = "100" THEN
						headerback <= "101";	
					ELSIF headerback = "101" THEN
						headerback <= "100";
					ELSE
						headerback <= "100";
					END IF;
				ELSE 
					calculate <= '0';
					headerback <= "111";
					error <= '1';
					state := nothing;
				END IF;
			ELSIF headerswitch = '1' AND i /= count AND calculate = '0' THEN
				headerswitch <= '0';
				IF n < 49 AND header = "0101" THEN
					numbercomplete((55-n) downto (49-n)) <= number;
					n <= n + 7;
					IF headerback = "100" THEN
						headerback <= "101";	
					ELSIF headerback = "101" THEN
						headerback <= "100";
					ELSE
						headerback <= "100";
					END IF;
				ELSIF n = 49 and header = "0101" THEN
					numbercomplete(6 downto 0) <= number;
					n <= 0;
					calculate <= '1';
					headerback <= "101";
				ELSE
					calculate <= '0';
					headerback <= "111";
					error <= '1';
					state := nothing;	
				END IF;
			END IF;
			IF i < count AND calculate = '1' THEN
			numberolddivide <= numberolddivide / resize(signed(number),11);
			i <= i + 1;
			ELSIF i = count THEN
				state := ready;
				numberold <= numberolddivide(59 downto 0);
				i <= 0;
			END IF;
		WHEN ready =>
			IF r < 48 THEN
				IF headerback = "101" AND header = "1010" THEN
					headerback <= "001";
					r <= r + 12;
				ELSIF headerback = "001" AND header = "1011" THEN
					headerback <= "101";
					r <= r + 12;
				--ELSE
					--headerback <= "001";
				END IF;
				result <= std_logic_vector(numberold((59-r) downto (48-r)));
			ELSIF r = 48 AND headerback = "101" AND header = "1010" THEN
				IF numberold(59) = '0' THEN
					negative <= '0';
				ELSIF numberold(59) = '1' THEN
					negative <= '1';
				END IF;
				headerback <= "001";
				result <= std_logic_vector(numberold(11 downto 0));
				shifting <= '1';
				postivenumber <= std_logic_vector(to_unsigned(to_integer(abs(signed(numberold))),numberold'LENGTH));
			ELSIF r = 48 AND header = "1100" THEN
				state := nothing;
				r <= 0;
			END IF;
			
			
			IF header = "1111" THEN
				state := nothing;
				perror <= '1';
			END IF;
			
		WHEN OTHERS => 
			state:= nothing;
			headerback <= "111";
			error <= '1';
		
	END CASE;
END IF;
END PROCESS;
PROCESS(clk)
BEGIN
IF reset = '0' THEN
		dig5 <= NOT "0000000";
		dig4 <= NOT "0111111";
		dig3 <= NOT "0111111";
		dig2 <= NOT "0111111";
		dig1 <= NOT "0111111";
		dig0 <= NOT "0111111";
		shift <= 0;
		ones <= "0000";
		tens <= "0000";
		hundreds <= "0000";
		thousands <= "0000";
		tenthousands <= "0000";
		shiftresult(59 downto 0) <= (others => '0');
		
ELSIF rising_edge(clk) THEN
		--Binary to BCD conversion
	IF unsigned(postivenumber) < 100000 AND error /= '1' THEN
		IF shift = 0 and shifting = '1' THEN	
			shiftresult(59 downto 0) <= std_logic_vector(shift_left(unsigned(postivenumber), 1));
			ones(0) <= postivenumber(59);
			ones(3 downto 1) <= "000";
			tens <= "0000";
			hundreds <= "0000";
			thousands <= "0000";
			tenthousands <= "0000";
			shift <= 1;
	
		ELSIF shift /= 0 and shift < 60 and shifting = '1' THEN
			-- Ones
			shiftresult(59 downto 0) <= std_logic_vector(shift_left(unsigned(shiftresult),1));
			IF shiftresult(59) = '1' AND ones >= 5 THEN
				ones <= "0001" + shift_left(ones + 3, 1);
			ELSIF shiftresult(59) = '1' AND ones < 5 THEN
				ones <= "0001" + shift_left(ones, 1);
			ELSIF shiftresult(59) = '0' AND ones >= 5 THEN
				ones <= shift_left(ones + 3, 1);
			ELSIF shiftresult(59) = '0' AND ones < 5 THEN
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
			--Tenthousands
			IF (thousands(3) = '1' or thousands >= 5) AND tenthousands >= 5 THEN					
				tenthousands <= "0001" + shift_left(tenthousands + 3, 1);
			ELSIF (thousands(3) = '1' or thousands >= 5) AND tenthousands < 5 THEN
				tenthousands <= "0001" + shift_left(tenthousands, 1);
			ELSIF thousands(3) = '0' AND thousands < 5 AND tenthousands >= 5 THEN
				tenthousands <= shift_left(tenthousands + 3, 1);
			ELSIF thousands(3) = '0' AND thousands < 5 AND tenthousands < 5 THEN
				tenthousands <= shift_left(tenthousands, 1);
			END IF;
			shift <= shift + 1;
		END IF;	

		IF shift = 60 and shifting = '1' THEN
			dig4 <= hex2display(std_logic_vector(tenthousands));
			dig3 <= hex2display(std_logic_vector(thousands));
			dig2 <= hex2display(std_logic_vector(hundreds));
			dig1 <= hex2display(std_logic_vector(tens));
			dig0 <= hex2display(std_logic_vector(ones));
			IF negative = '1' THEN
			dig5 <= NOT "1000000";
			ELSIF negative = '0' THEN
			dig5 <= NOT "0000000";
			END IF;
			shift <= 0;
		END IF;

	ELSE IF unsigned(postivenumber) > 100000 AND error /= '1' AND shifting = '1' THEN
		dig0 <= NOT "1110110";
		dig1 <= NOT "0111101";
		dig2 <= NOT "0111110";
		dig3 <= NOT "0111111";
		dig4 <= NOT "0110111";
		dig5 <= NOT "1111001";
	END IF;
	
	IF error = '1' THEN
		dig0 <= NOT "1010000";
		dig1 <= NOT "1011100";
		dig2 <= NOT "1010000";
		dig3 <= NOT "1010000";
		dig4 <= NOT "1111001";
		dig5 <= NOT "0000000";
	END IF;	
	
	IF perror = '1' THEN
		dig0 <= NOT "1010000";
		dig1 <= NOT "1011100";
		dig2 <= NOT "1010000";
		dig3 <= NOT "1010000";
		dig4 <= NOT "1111001";
		dig5 <= NOT "1110011";
	END IF;	
	
END IF;
END IF;
END PROCESS;
END calculate;




