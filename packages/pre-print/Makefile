TEX      = pdflatex
BIB      = bibtex
MAIN     = ms
UV       = uv

# Canonical figures are generated into the repository-level assets/ directory by
# the `experiments` package CLI (a PNG for the docs site, a PDF for the paper).
# The PDFs are copied in here at build time so the manuscript -- and its
# submission tarball -- stay self-contained and never reference paths outside
# this directory.
ASSETSDIR = ../../assets/figures
FIGURES   = form-factor.pdf provenance-bias.pdf resonance-overlap.pdf trapped-weight.pdf trapping-cap.pdf crossover-bias.pdf finite-thickness.pdf balescu-lenard.pdf

.PHONY: all clean distclean figures submission test-particle test-particle-simulate

all: figures $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex $(MAIN).bib $(FIGURES)
	$(TEX) $(MAIN)
	$(BIB) $(MAIN)
	$(TEX) $(MAIN)
	$(TEX) $(MAIN)

# Generate the canonical figure set into assets/, then copy the PDFs in here.
figures $(FIGURES):
	cd ../.. && $(UV) run experiments figures
	cp $(addprefix $(ASSETSDIR)/,$(FIGURES)) .

# The test-particle validation figure (test-particle-bias.pdf) comes from an
# expensive, stochastic orbit-integration experiment. Results are cached in
# assets/data/test-particle-data.json; `simulate` (re)computes the full set or adds
# points (e.g. --alpha 0.6), and `plot` re-draws cheaply from the cache.
test-particle-simulate:
	cd ../.. && $(UV) run experiments test-particle-simulate --store assets/data/test-particle-data.json
test-particle:
	cd ../.. && $(UV) run experiments test-particle-plot --store assets/data/test-particle-data.json
	cp $(ASSETSDIR)/test-particle-bias.pdf .

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
	rm -f $(MAIN).pdf $(FIGURES) test-particle-bias.pdf
