# RedTwin -- NSF 26-506 (PESOSE) Track 3
.PHONY: all check clean facilities mentoring

all: main.pdf facilities mentoring

main.pdf: main.tex references.bib $(wildcard sections/*.tex) figures/redtwin_architecture.pdf
	pdflatex -interaction=nonstopmode main.tex
	bibtex main
	pdflatex -interaction=nonstopmode main.tex
	pdflatex -interaction=nonstopmode main.tex

check: main.pdf
	@python3 check.py

facilities: documents/facilities.pdf

documents/facilities.pdf: documents/facilities.tex
	cd documents && pdflatex -interaction=nonstopmode facilities.tex
	cd documents && pdflatex -interaction=nonstopmode facilities.tex

mentoring: documents/mentoring_plan.pdf

documents/mentoring_plan.pdf: documents/mentoring_plan.tex
	cd documents && pdflatex -interaction=nonstopmode mentoring_plan.tex

clean:
	rm -f main.aux main.bbl main.blg main.log main.out
	rm -f documents/facilities.aux documents/facilities.log documents/facilities.out
	rm -f documents/mentoring_plan.aux documents/mentoring_plan.log documents/mentoring_plan.out
