#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, \
    redirect, url_for, flash, request, current_app
from flask_login import current_user
from ..decorators import company_required
from ..forms import RegisterCompanyForm, CompanyDetailForm
from ..models import Company, Job

company = Blueprint('company', __name__, url_prefix='/company')


@company.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('front.index'))
    form = RegisterCompanyForm()
    if form.validate_on_submit():
        form.create_company()
        flash('注册成功，请登录', 'success')
        return redirect(url_for('front.login'))
    return render_template('company/register.html', form=form, active='company_register')


@company.route('/')
def index():
    page = request.args.get('page', default=1, type=int)
    pagination = Company.query.order_by(Company.updated_at.desc()).paginate(
        page=page, per_page=current_app.config['COMPANY_INDEX_PER_PAGE'], error_out=False)
    return render_template('company/index.html', pagination=pagination, active='company')


@company.route('/<int:company_id>')
def detail(company_id):
    company_data = Company.query.get_or_404(company_id)
    if request.args.get('job'):
        page = request.args.get('page', default=1, type=int)
        pagination = company_data.jobs.order_by(Job.updated_at.desc()).paginate(
            page=page, per_page=current_app.config['LIST_PER_PAGE'], error_out=False)
        return render_template('company/detail.html', pagination=pagination, panel='jobs', company=company_data)
    return render_template('company/detail.html', company=company_data, panel='about')


@company.route('/account', methods=['GET', 'POST'])
@company_required
def edit():
    form = CompanyDetailForm(obj=current_user)
    if form.validate_on_submit():
        form.update_detail(current_user)
        flash('公司信息更新成功', 'success')
    return render_template('company/edit.html', form=form, active='edit')


@company.route('/jobs')
@company_required
def jobs():
    page = request.args.get('page', default=1, type=int)
    pagination = current_user.jobs.order_by(Job.updated_at.desc()).paginate(
        page=page, per_page=current_app.config['LIST_PER_PAGE'], error_out=False)
    return render_template('company/jobs.html', pagination=pagination, active='jobs')


@company.route('/resumes')
@company_required
def resumes():
    page = request.args.get('page', default=1, type=int)
    pagination = current_user.resumes.order_by(Job.updated_at.desc()).paginate(
        page=page, per_page=current_app.config['LIST_PER_PAGE'], error_out=False)
    return render_template('company/resumes.html', pagination=pagination, active='resumes')


@company.route('/resume/accept')
@company_required
def resume_accept():
    page = request.args.get('page', default=1, type=int)
    pagination = current_user.resumes.order_by(Job.updated_at.desc()).paginate(
        page=page, per_page=current_app.config['LIST_PER_PAGE'], error_out=False)
    return render_template('company/resumes.html', pagination=pagination, active='resumes')


@company.route('/resume/reject')
@company_required
def resume_reject():
    page = request.args.get('page', default=1, type=int)
    pagination = current_user.resumes.order_by(Job.updated_at.desc()).paginate(
        page=page, per_page=current_app.config['LIST_PER_PAGE'], error_out=False)
    return render_template('company/resumes.html', pagination=pagination, active='resumes')