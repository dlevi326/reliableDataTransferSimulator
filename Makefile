INPUT ?= ./file_1MB.txt
OUTPUT ?= ./output.txt


test:
	python receiver.py & time python sender.py < $(INPUT) &
diff:
	diff $(INPUT) $(OUTPUT)
kill:
	pkill python
clean:
	rm *.log $(OUTPUT) *.pyc
