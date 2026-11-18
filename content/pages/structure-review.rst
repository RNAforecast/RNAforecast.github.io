RNA structure review
####################

:title: RNA structure review, RNA Forecast
:slug: structure-review
:description: A planned format for commissioned scientific assessments of predicted RNA structures before synthesis or publication. In development.
:referrer: no-referrer-when-downgrade
:summary: A planned format for commissioned scientific assessments of predicted RNA structures, documented so that they hold up in a manuscript, a grant or a design meeting. In development.
:og_type: website
:hero_kicker: In development
:hero_title: RNA structure review
:hero_lead: A secondary structure prediction takes a second. The decisions built on it, a synthesis run, a mutant series, a figure in a grant, cost months. RNA Forecast is developing a format for commissioned scientific assessments that will read the prediction the way a code review reads code, state what is supported and by what, and be documented so that they hold up in a manuscript, a grant or a design meeting.
:hero_actions: `Receive the launch announcement <#announcement>`__ `What a review will contain <#what-a-review-will-contain>`__

.. container:: lead

  The review format is in development. RNA Forecast is not accepting review
  commissions at this stage. Details will be published when the format
  launches.

  An RNA structure review will be scientific work. It will evaluate
  computational results with the published methods of the field and be
  written by Michael T. Wolfinger, co-developer of the ViennaRNA Package, who has worked on RNA
  structure and its interpretation since 2000.

  The planned format is a commissioned assessment for a defined question.
  It will not be a collaboration and will carry no co-authorship. The group
  will keep the document and its results. Scope, terms and
  availability will be published when the format launches.

  What a wrong structure costs a project, worked through on real sequences,
  is in
  `What a wrong RNA structure costs <https://michaelwolfinger.com/blog/2026/what-a-wrong-rna-structure-costs/?utm_source=rnaforecast.com&utm_medium=referral&utm_campaign=structure-review>`__.

.. _what-a-review-will-contain:

What a review will contain
--------------------------

.. container:: split

  .. container:: split-main

    A written document on the sequence or the set of sequences in question,
    which will state for the question asked

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

    **When a review will be worth it.** Before modified mRNAs go to
    synthesis. Before a mutant series designed against a helix. Before a
    structure figure goes into a manuscript or a grant application. When
    probing data and prediction disagree. When a design has to keep its
    structure under sequence changes.

    **What it will not be.** Tertiary structure prediction, wet-lab work,
    project management, or a promise about how the molecule behaves in a
    cell. A review will say how far the computation carries the question and
    where the evidence has to come from somewhere else.

    Groups that would rather learn to do this themselves will find the same
    questions in `ViennaRNA training from the developers </training/#viennarna>`__.

  .. container:: blueprint

    .. container:: kicker-sm

      Launch announcement

    .. raw:: html

      <form class="contact-form" method="post" id="announcement"
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
        <p class="form-note">You get one e-mail when the format launches, and nothing else. A reply to that e-mail takes you off the list.</p>
        <button class="btn btn-primary btn-block" type="submit">Receive the launch announcement</button>
        <p class="form-note form-fallback">Problems with the form? Email
          <a href="mailto:hello@rnaforecast.com">hello&#64;rnaforecast.com</a>.</p>
      </form>
