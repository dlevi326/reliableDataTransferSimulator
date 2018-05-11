INPUT ?= ./file_4bytes.txt
OUTPUT ?= ./output.txt


test:
	python receiver.py > $(OUTPUT) & time python sender.py < $(INPUT) &
diff:
	diff $(INPUT) $(OUTPUT)
kill:
	pkill python
clean:
	rm *.log $(OUTPUT) *.pyc
