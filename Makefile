# RedTwin -- NSF 26-506 (PESOSE) Track 3
.PHONY: all check clean

all: main.pdf

main.pdf: main.tex references.bib $(wildcard sections/*.tex) figures/redtwin_architecture.pdf
	pdflatex -interaction=nonstopmode main.tex
	bibtex main
	pdflatex -interaction=nonstopmode main.tex
	pdflatex -interaction=nonstopmode main.tex

check: main.pdf
	@python3 check.py

clean:
	rm -f main.aux main.bbl main.blg main.log main.out
