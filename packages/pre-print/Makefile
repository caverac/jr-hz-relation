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

OUTDIR   = /tmp/jr-hz-relation
STAGEDIR = $(OUTDIR)/submission
TARFILE  = $(OUTDIR)/jr-hz-relation-preprint.tar

# AAS policy (https://journals.aas.org/manuscript-preparation/#linenumber) asks
# for line numbers on the manuscript so reviewers can cite locations. Rather than
# carry the `linenumbers` class option in the canonical source -- which would put
# line numbers on every `make all` build and the docs site -- the submission
# target injects it into a *staged* copy of $(MAIN).tex and compiles that.
# aastex701's `linenumbers` option pulls in the lineno package and handles the
# two-column layout, so both the uploaded .tex and its PDF carry line numbers
# while the everyday build stays clean. Ships the prebuilt .bbl, so two pdflatex
# passes (no bibtex) suffice to resolve citations and line-number references.
submission: all
	@rm -rf $(STAGEDIR)
	@mkdir -p $(STAGEDIR)
	@sed -E 's/(\\documentclass\[[^]]*)\](\{aastex701\})/\1,linenumbers]\2/' $(MAIN).tex > $(STAGEDIR)/$(MAIN).tex
	@cp $(MAIN).bib $(MAIN).bbl $(STAGEDIR)/
	@cp $(addprefix $(ASSETSDIR)/,$(FIGURES)) $(STAGEDIR)/
	@cd $(STAGEDIR) && $(TEX) -interaction=nonstopmode -halt-on-error $(MAIN) && $(TEX) -interaction=nonstopmode -halt-on-error $(MAIN)
	@COPYFILE_DISABLE=1 tar cf $(TARFILE) -C $(STAGEDIR) $(MAIN).tex $(MAIN).bbl $(MAIN).pdf $(FIGURES)
	@echo "Created $(TARFILE) (line-numbered submission)"

clean:
	rm -f $(MAIN).aux $(MAIN).bbl $(MAIN).blg $(MAIN).log $(MAIN).out
	rm -f $(MAIN).fdb_latexmk $(MAIN).fls $(MAIN).synctex.gz $(MAIN).toc

distclean: clean
	rm -f $(MAIN).pdf $(FIGURES)
