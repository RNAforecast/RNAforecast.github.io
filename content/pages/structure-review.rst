RNA structure review
####################

:title: RNA structure review, RNA Forecast
:slug: structure-review
:description: A commissioned scientific assessment of a predicted RNA structure before synthesis, mutagenesis or publication. RNA Forecast, in preparation.
:referrer: no-referrer-when-downgrade
:summary: A commissioned scientific assessment of a predicted RNA structure before anything is built on it, documented so that it holds up in a manuscript, a grant or a design meeting. In preparation.
:og_type: website
:hero_kicker: In preparation
:hero_title: RNA structure review
:hero_lead: A secondary structure prediction takes a second. The decisions built on it, a synthesis run, a mutant series, a figure in a grant, cost months. RNA Forecast is preparing commissioned scientific assessments that read the prediction the way a code review reads code, state what is supported and by what, and are documented so that they hold up in a manuscript, a grant or a design meeting.
:hero_actions: `Pre-register <#pre-register>`__ `What a review contains <#what-a-review-contains>`__

.. container:: lead

  An RNA structure review is scientific work. It evaluates computational
  results with the published methods of the field and is written by Michael T.
  Wolfinger, co-developer of the ViennaRNA Package, who has worked on RNA
  structure and its interpretation since 2000.

  A review is commissioned by a group for a defined question. It is not a
  collaboration and carries no co-authorship. The group keeps the document
  and its results. Scope and terms are agreed before any work starts.

  What a wrong structure costs a project, worked through on real sequences,
  is in
  `What a wrong RNA structure costs <https://michaelwolfinger.com/blog/2026/what-a-wrong-rna-structure-costs/?utm_source=rnaforecast.com&utm_medium=referral&utm_campaign=structure-review>`__.

.. _what-a-review-contains:

What a review contains
----------------------

.. container:: split

  .. container:: split-main

    A written document on the sequence or the set of sequences in question,
    which states for the question asked

    - which helices of the predicted structure are supported, and by what,
      i.e. base pair probabilities, ensemble diversity, suboptimal structures,
      conservation where homologues exist, probing data where there are any
    - where the ensemble disagrees with the single structure in the figure,
      and whether that disagreement touches the region the question is about
    - what the model does not contain for this molecule, e.g. modified
      nucleotides, ions, proteins, tertiary contacts, and whether that matters
      for the decision at hand
    - which observation would contradict the interpretation, so that the next
      experiment is chosen to settle something
    - the methods and software versions, named as in a methods section, so
      that the assessment can be cited

    **When a review is worth it.** Before modified mRNAs go to
    synthesis. Before a mutant series designed against a helix. Before a
    structure figure goes into a manuscript or a grant application. When
    probing data and prediction disagree. When a design has to keep its
    structure under sequence changes.

    **What it is not.** Tertiary structure prediction, wet-lab work, project
    management, or a promise about how the molecule behaves in a cell. A review says how far
    the computation carries the question and where the evidence has to come
    from somewhere else.

    Groups that would rather learn to do this themselves will find the same
    questions in `ViennaRNA training from the developers </training/#viennarna>`__.

  .. container:: blueprint

    .. container:: kicker-sm

      Pre-register

    .. raw:: html

      <form class="contact-form" method="post" id="pre-register"
            action="https://forms.rnaforecast.com/rnaf-waitlist-review">
        <p class="form-error" id="review-error">Something was missing or not valid. Please check the fields and send again.</p>
        <input type="hidden" name="topic" value="structure-review" />
        <input class="hp" type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true" />
        <p class="field">
          <label for="review-name">Name</label>
          <input class="input" type="text" id="review-name" name="name"
                 autocomplete="name" />
        </p>
        <p class="field">
          <label for="review-email">Email <abbr title="required">*</abbr></label>
          <input class="input" type="email" id="review-email" name="email"
                 autocomplete="email" required />
        </p>
        <p class="field">
          <label for="review-organization">Affiliation</label>
          <input class="input" type="text" id="review-organization" name="organization"
                 autocomplete="organization" placeholder="Institute, company or group" />
        </p>
        <p class="field">
          <label for="review-role">You are</label>
          <select class="input" id="review-role" name="role">
            <option value="">Choose one</option>
            <option value="experimental-lab">An experimental lab</option>
            <option value="computational-group">A computational group</option>
            <option value="biotech-industry">Biotech or industry</option>
            <option value="doctoral-programme">A doctoral programme or course</option>
            <option value="tool-developer">A tool developer</option>
            <option value="other">Something else</option>
          </select>
        </p>
        <p class="field">
          <label for="review-wish">What would you want reviewed?</label>
          <textarea class="input" id="review-wish" name="wishes" rows="3"
                    placeholder="The molecule, and the decision that depends on its structure"></textarea>
        </p>
        <p class="form-note">You get one e-mail when reviews open, with the terms, and nothing else. A reply to that e-mail takes you off the list.</p>
        <button class="btn btn-primary btn-block" type="submit">Pre-register</button>
        <p class="form-note form-fallback">Problems with the form? Email
          <a href="mailto:hello@rnaforecast.com">hello&#64;rnaforecast.com</a>.</p>
      </form>
