# RedTwin -- NSF 26-506 (PESOSE) Track 3

.PHONY: all check docs clean

# `make` builds the proposal only. The supplementary documents are built on
# request, with `make docs`.
all: main.pdf

main.pdf: main.tex references.bib $(wildcard sections/*.tex) figures/redtwin_architecture.pdf
	pdflatex -interaction=nonstopmode main.tex
	bibtex main
	pdflatex -interaction=nonstopmode main.tex
	pdflatex -interaction=nonstopmode main.tex

check: main.pdf
	@python3 check.py

# ---- Supplementary documents (Facilities, Mentoring Plan, ...) -------------
# On demand: `make docs`, or `make documents/facilities.pdf` for just one.
# Every .tex in documents/ is a standalone document, so new ones are picked up
# automatically. The .docx and the Research.gov DMP print are maintained
# outside LaTeX and are not built here.
DOC_TEX := $(wildcard documents/*.tex)
DOC_PDF := $(DOC_TEX:.tex=.pdf)
LATEX   := pdflatex -interaction=nonstopmode -halt-on-error

docs: $(DOC_PDF)

# Second pass only when LaTeX asks for one, so the common case stays fast.
documents/%.pdf: documents/%.tex
	cd documents && $(LATEX) $*.tex
	@if grep -qs 'Rerun to get' documents/$*.log; then cd documents && $(LATEX) $*.tex; fi

clean:
	rm -f main.aux main.bbl main.blg main.log main.out
	rm -f documents/*.aux documents/*.log documents/*.out
