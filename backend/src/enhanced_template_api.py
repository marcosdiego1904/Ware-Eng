"""
Enhanced Template API with Privacy Controls and Organization Support
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from database import db
from auth import token_required
from enhanced_template_models import (
    EnhancedWarehouseTemplate, 
    TemplateCategory, 
    Organization,
    TemplatePermission,
    TemplateReview
)
from models import WarehouseConfig
from sqlalchemy import and_, or_

enhanced_template_bp = Blueprint('enhanced_templates', __name__, url_prefix='/api/v1/templates')

@enhanced_template_bp.route('/', methods=['GET'])
@cross_origin()
@token_required
def list_templates(current_user):
    """
    Get templates with enhanced privacy filtering
    Query params: scope, category, industry, search, featured, page, per_page
    """
    try:
        # Get query parameters
        scope = request.args.get('scope', 'accessible')  # accessible, my, company, public, all
        category = request.args.get('category')
        industry = request.args.get('industry')  
        search = request.args.get('search')
        featured = request.args.get('featured', '').lower() == 'true'
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        # Base query
        query = EnhancedWarehouseTemplate.query.filter_by(is_active=True)
        
        # Apply scope filtering
        if scope == 'my':
            query = query.filter_by(created_by=current_user.id)
        elif scope == 'company':
            if hasattr(current_user, 'organization_id') and current_user.organization_id:
                # Get templates from same organization
                company_users = db.session.query(User.id).filter_by(
                    organization_id=current_user.organization_id
                ).subquery()
                query = query.filter(
                    and_(
                        EnhancedWarehouseTemplate.created_by.in_(company_users),
                        or_(
                            EnhancedWarehouseTemplate.visibility == 'COMPANY',
                            EnhancedWarehouseTemplate.visibility == 'PUBLIC',
                            EnhancedWarehouseTemplate.created_by == current_user.id
                        )
                    )
                )
            else:
                # User has no organization, show only their own templates
                query = query.filter_by(created_by=current_user.id)
        elif scope == 'public':
            query = query.filter_by(visibility='PUBLIC')
        elif scope == 'accessible':
            # Show templates user can access based on privacy rules
            if hasattr(current_user, 'organization_id') and current_user.organization_id:
                # Get company users for company template access
                company_users = db.session.query(User.id).filter_by(
                    organization_id=current_user.organization_id
                ).subquery()
                
                query = query.filter(
                    or_(
                        # Own templates
                        EnhancedWarehouseTemplate.created_by == current_user.id,
                        # Public templates
                        EnhancedWarehouseTemplate.visibility == 'PUBLIC',
                        # Company templates from same organization
                        and_(
                            EnhancedWarehouseTemplate.visibility == 'COMPANY',
                            EnhancedWarehouseTemplate.created_by.in_(company_users)
                        ),
                        # Explicitly shared templates
                        EnhancedWarehouseTemplate.permissions.any(
                            TemplatePermission.user_id == current_user.id
                        )
                    )
                )
            else:
                query = query.filter(
                    or_(
                        EnhancedWarehouseTemplate.created_by == current_user.id,
                        EnhancedWarehouseTemplate.visibility == 'PUBLIC'
                    )
                )
        
        # Apply additional filters
        if category:
            query = query.filter_by(template_category=category)
        
        if industry:
            query = query.filter_by(industry_category=industry)
        
        if featured:
            query = query.filter_by(featured=True)
        
        if search:
            search_filter = or_(
                EnhancedWarehouseTemplate.name.ilike(f'%{search}%'),
                EnhancedWarehouseTemplate.description.ilike(f'%{search}%'),
                EnhancedWarehouseTemplate.tags.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # Order by featured first, then rating, then usage
        query = query.order_by(
            EnhancedWarehouseTemplate.featured.desc(),
            EnhancedWarehouseTemplate.rating.desc(),
            EnhancedWarehouseTemplate.downloads_count.desc(),
            EnhancedWarehouseTemplate.created_at.desc()
        )
        
        # Paginate
        paginated = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Get summary statistics
        stats = {
            'my_templates': EnhancedWarehouseTemplate.query.filter_by(
                created_by=current_user.id, 
                is_active=True
            ).count(),
            'public_templates': EnhancedWarehouseTemplate.query.filter_by(
                visibility='PUBLIC',
                is_active=True
            ).count(),
            'total_accessible': query.count()
        }
        
        return jsonify({
            'templates': [template.to_dict() for template in paginated.items],
            'pagination': {
                'page': paginated.page,
                'pages': paginated.pages,
                'per_page': paginated.per_page,
                'total': paginated.total,
                'has_next': paginated.has_next,
                'has_prev': paginated.has_prev
            },
            'stats': stats,
            'scope': scope
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch templates: {str(e)}'}), 500

@enhanced_template_bp.route('/categories', methods=['GET'])
@cross_origin()
@token_required
def get_template_categories(current_user):
    """Get all template categories"""
    try:
        categories = TemplateCategory.query.filter_by(is_active=True).order_by(
            TemplateCategory.sort_order
        ).all()
        
        return jsonify({
            'categories': [category.to_dict() for category in categories]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch categories: {str(e)}'}), 500

@enhanced_template_bp.route('/create-from-config', methods=['POST'])
@cross_origin()
@token_required
def create_template_from_config(current_user):
    """
    Create a new template from existing warehouse configuration
    """
    try:
        data = request.get_json()
        config_id = data.get('config_id')
        name = data.get('name')
        description = data.get('description', '')
        visibility = data.get('visibility', 'PRIVATE')
        template_category = data.get('template_category', 'CUSTOM')
        industry_category = data.get('industry_category')
        tags = data.get('tags', [])
        
        if not config_id or not name:
            return jsonify({'error': 'Config ID and name are required'}), 400
        
        # Get the warehouse config
        config = WarehouseConfig.query.get_or_404(config_id)
        
        # Validate visibility
        if visibility not in ['PRIVATE', 'COMPANY', 'PUBLIC']:
            return jsonify({'error': 'Invalid visibility setting'}), 400
        
        # Create template
        template = EnhancedWarehouseTemplate(
            name=name,
            description=description,
            num_aisles=config.num_aisles,
            racks_per_aisle=config.racks_per_aisle,
            positions_per_rack=config.positions_per_rack,
            levels_per_position=config.levels_per_position,
            level_names=config.level_names,
            default_pallet_capacity=config.default_pallet_capacity,
            bidimensional_racks=config.bidimensional_racks,
            receiving_areas_template=config.receiving_areas,
            staging_areas_template=config.staging_areas,
            dock_areas_template=config.dock_areas,
            visibility=visibility,
            template_category=template_category,
            industry_category=industry_category,
            based_on_config_id=config.id,
            created_by=current_user.id,
            # Set company_id if creating company template
            company_id=current_user.organization.organization_code if visibility == 'COMPANY' and hasattr(current_user, 'organization') and current_user.organization else None
        )
        
        # Set tags
        template.set_tags(tags)
        
        # Generate unique template code
        template.generate_template_code()
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'message': 'Template created successfully',
            'template': template.to_dict(include_sensitive=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create template: {str(e)}'}), 500

@enhanced_template_bp.route('/<int:template_id>/share', methods=['POST'])
@cross_origin()
@token_required
def share_template(current_user, template_id):
    """
    Share template with specific users or change visibility
    """
    try:
        template = EnhancedWarehouseTemplate.query.get_or_404(template_id)
        
        # Check if user owns the template
        if template.created_by != current_user.id:
            return jsonify({'error': 'Only template creator can share templates'}), 403
        
        data = request.get_json()
        action = data.get('action')  # 'change_visibility' or 'share_with_users'
        
        if action == 'change_visibility':
            new_visibility = data.get('visibility')
            if new_visibility not in ['PRIVATE', 'COMPANY', 'PUBLIC']:
                return jsonify({'error': 'Invalid visibility setting'}), 400
            
            template.visibility = new_visibility
            template.is_public = (new_visibility == 'PUBLIC')  # Legacy compatibility
            
            # Set company_id for company templates
            if new_visibility == 'COMPANY' and hasattr(current_user, 'organization') and current_user.organization:
                template.company_id = current_user.organization.organization_code
            elif new_visibility != 'COMPANY':
                template.company_id = None
                
        elif action == 'share_with_users':
            user_ids = data.get('user_ids', [])
            permission_type = data.get('permission_type', 'VIEW')
            
            for user_id in user_ids:
                # Check if permission already exists
                existing = TemplatePermission.query.filter_by(
                    template_id=template.id,
                    user_id=user_id
                ).first()
                
                if not existing:
                    permission = TemplatePermission(
                        template_id=template.id,
                        user_id=user_id,
                        permission_type=permission_type,
                        granted_by=current_user.id
                    )
                    db.session.add(permission)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Template sharing updated successfully',
            'template': template.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update sharing: {str(e)}'}), 500

@enhanced_template_bp.route('/<int:template_id>/review', methods=['POST'])
@cross_origin()
@token_required
def add_template_review(current_user, template_id):
    """Add or update a template review"""
    try:
        template = EnhancedWarehouseTemplate.query.get_or_404(template_id)
        
        # Check if user can access this template
        if not template.can_user_access(current_user):
            return jsonify({'error': 'Template not accessible'}), 403
        
        data = request.get_json()
        rating = data.get('rating')
        review_text = data.get('review_text', '')
        
        if not rating or rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        # Check if user already reviewed this template
        existing_review = TemplateReview.query.filter_by(
            template_id=template.id,
            user_id=current_user.id
        ).first()
        
        if existing_review:
            # Update existing review
            existing_review.rating = rating
            existing_review.review_text = review_text
        else:
            # Create new review
            review = TemplateReview(
                template_id=template.id,
                user_id=current_user.id,
                rating=rating,
                review_text=review_text
            )
            db.session.add(review)
        
        # Recalculate template rating
        template.calculate_rating()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Review added successfully',
            'template_rating': float(template.rating)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add review: {str(e)}'}), 500

@enhanced_template_bp.route('/<int:template_id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_enhanced_template(current_user, template_id):
    """
    Delete a template (soft delete) - Enhanced version with better permission checking
    """
    try:
        template = EnhancedWarehouseTemplate.query.get_or_404(template_id)
        
        # Check if user owns the template
        if template.created_by != current_user.id:
            return jsonify({'error': 'Access denied. You can only delete your own templates'}), 403
        
        # Soft delete
        template.is_active = False
        db.session.commit()
        
        return jsonify({
            'message': 'Template deleted successfully',
            'template_id': template_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete template: {str(e)}'}), 500