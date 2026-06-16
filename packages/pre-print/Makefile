TEX      = pdflatex
BIB      = bibtex
MAIN     = ms

# Figures are NOT generated here. The canonical figure set (and the test-particle
# data behind it) is produced by the `experiments` package CLI, run from the repo
# root -- e.g. `uv run experiments figures` and `uv run experiments
# test-particle-plot` -- which writes a PNG (docs site) and a PDF (paper) into
# assets/figures/. This Makefile only *syncs* (copies) the finished PDFs in here, so
# the manuscript -- and its submission tarball -- stay self-contained.
ASSETSDIR = ../../assets/figures
FIGURES   = form-factor.pdf provenance-bias.pdf resonance-overlap.pdf trapped-weight.pdf trapping-cap.pdf crossover-bias.pdf finite-thickness.pdf balescu-lenard.pdf test-particle-bias.pdf

.PHONY: all clean distclean sync-figures submission

all: sync-figures $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex $(MAIN).bib $(FIGURES)
	$(TEX) $(MAIN)
	$(BIB) $(MAIN)
	$(TEX) $(MAIN)
	$(TEX) $(MAIN)

# Copy the finished figure PDFs from assets/figures/ into this directory. Figures
# must already exist there; regenerate them from the repo root with the experiments
# CLI (see the note above), never from this folder.
sync-figures $(FIGURES):
	cp $(addprefix $(ASSETSDIR)/,$(FIGURES)) .

OUTDIR  = /tmp/jr-hz-relation
TARFILE = $(OUTDIR)/jr-hz-relation-preprint.tar

submission: all
	@mkdir -p $(OUTDIR)
	@COPYFILE_DISABLE=1 tar cf $(TARFILE) $(MAIN).tex $(MAIN).bbl $(MAIN).pdf $(FIGURES)
	@echo "Created $(TARFILE)"

clean:
	rm -f $(MAIN).aux $(MAIN).bbl $(MAIN).blg $(MAIN).log $(MAIN).out
	rm -f $(MAIN).fdb_latexmk $(MAIN).fls $(MAIN).synctex.gz $(MAIN).toc

distclean: clean
	rm -f $(MAIN).pdf $(FIGURES)
