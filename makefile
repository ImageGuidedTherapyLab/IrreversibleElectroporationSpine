# Makefile for generating presentation $(TARGET).pdf from $(TARGET).tex 
PAPER = ireMethods

.PHONY: $(PAPER).pdf 
all: $(PAPER).pdf

# build pdf file first to ensure all aux files are available
# http://latex2rtf.sourceforge.net/
#   M6 converts equations to bitmaps
$(PAPER).rtf: $(PAPER).pdf $(PAPER).bbl $(PAPER).aux
	latex2rtf -M12 -D 600 $(PAPER).tex

$(PAPER).pdf: $(PAPER).tex $(PAPER).bbl
	pdflatex $(PAPER).tex

$(PAPER).bbl: $(PAPER).bib 
	pdflatex $(PAPER).tex
	bibtex $(PAPER)
	pdflatex $(PAPER).tex

# build pdf file first to ensure all aux files are available
$(PAPER).dvi: $(PAPER).pdf 
	latex $(PAPER).tex

cover: cover_letter.tex
	pdflatex cover_letter.tex 

clean:
	rm $(PAPER).aux  $(PAPER).dvi $(PAPER).pdf $(PAPER).bbl  $(PAPER).log  $(PAPER).blg  $(PAPER).out

